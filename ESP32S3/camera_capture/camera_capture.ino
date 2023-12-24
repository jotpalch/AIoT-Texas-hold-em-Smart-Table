#include "esp_camera.h"
#include <WiFi.h>
#define SERVER      "pokerimg.jotpac.com"  // 請改成你的網站伺服器位址或域名
#define UPLOAD_URL  "/esp32cam"
#define PORT        80
//
// WARNING!!! PSRAM IC required for UXGA resolution and high JPEG quality
//            Ensure ESP32 Wrover Module or other board with PSRAM is selected
//            Partial images will be transmitted if image exceeds buffer size
//
//            You must select partition scheme from the board menu that has at least 3MB APP space.
//            Face Recognition is DISABLED for ESP32 and ESP32-S2, because it takes up from 15 
//            seconds to process single frame. Face Detection is ENABLED if PSRAM is enabled as well

// ===================
// Select camera model
// ===================
//#define CAMERA_MODEL_WROVER_KIT // Has PSRAM
//#define CAMERA_MODEL_ESP_EYE // Has PSRAM
#define CAMERA_MODEL_ESP32S3_EYE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_PSRAM // Has PSRAM
//#define CAMERA_MODEL_M5STACK_V2_PSRAM // M5Camera version B Has PSRAM
//#define CAMERA_MODEL_M5STACK_WIDE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_ESP32CAM // No PSRAM
//#define CAMERA_MODEL_M5STACK_UNITCAM // No PSRAM
//#define CAMERA_MODEL_AI_THINKER // Has PSRAM
//#define CAMERA_MODEL_TTGO_T_JOURNAL // No PSRAM
//#define CAMERA_MODEL_XIAO_ESP32S3 // Has PSRAM
// ** Espressif Internal Boards **
//#define CAMERA_MODEL_ESP32_CAM_BOARD
//#define CAMERA_MODEL_ESP32S2_CAM_BOARD
//#define CAMERA_MODEL_ESP32S3_CAM_LCD
//#define CAMERA_MODEL_DFRobot_FireBeetle2_ESP32S3 // Has PSRAM
//#define CAMERA_MODEL_DFRobot_Romeo_ESP32S3 // Has PSRAM
#include "camera_pins.h"

// ===========================
// Enter your WiFi credentials
// ===========================
const char* ssid = "DCSlab_2.4G";
const char* password = "!@#$dcswifi4share";

WiFiClient client;
void startCameraServer();
void setupLedFlash(int pin);

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG; // for streaming
  //config.pixel_format = PIXFORMAT_RGB565; // for face detection/recognition
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;
  
  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  //                      for larger pre-allocated frame buffer.
  if(config.pixel_format == PIXFORMAT_JPEG){
    if(psramFound()){
      config.jpeg_quality = 10;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      // Limit the frame size when PSRAM is not available
      config.frame_size = FRAMESIZE_SVGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    // Best option for face detection/recognition
    config.frame_size = FRAMESIZE_240X240;
#if CONFIG_IDF_TARGET_ESP32S3
    config.fb_count = 2;
#endif
  }

#if defined(CAMERA_MODEL_ESP_EYE)
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
#endif

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t * s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1); // flip it back
    s->set_brightness(s, 1); // up the brightness just a bit
    s->set_saturation(s, -2); // lower the saturation
  }
  // drop down frame size for higher initial frame rate
  if(config.pixel_format == PIXFORMAT_JPEG){
    s->set_framesize(s, FRAMESIZE_QVGA);
  }

#if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
#endif

#if defined(CAMERA_MODEL_ESP32S3_EYE)
  s->set_vflip(s, 1);
#endif

// Setup LED FLash if LED pin is defined in camera_pins.h
#if defined(LED_GPIO_NUM)
  setupLedFlash(LED_GPIO_NUM);
#endif

  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");

  s->set_vflip(s, 0);
  s->set_framesize(s, FRAMESIZE_VGA) ;
  s->set_brightness(s, 2); // up the brightness just a bit
  //s->set_saturation(s, -2); // lower the saturation
  Serial.println("Set camera") ;
} // setup()

void postImage() {
  camera_fb_t *fb = NULL;    // 宣告儲存影像結構資料的變數
  fb = esp_camera_fb_get();  // 拍照

  if(!fb) {
    Serial.println("無法取得影像資料…");
    delay(1000);
    ESP.restart();  // 重新啟動
  }

  Serial.printf("連接伺服器：%s\n", SERVER);

  if (client.connect(SERVER, PORT)) {
    Serial.println("開始上傳影像…");     

    String boundBegin = "--ESP32CAM\r\n";
    boundBegin += "Content-Disposition: form-data; name=\"filename\"; filename=\"pict.jpg\"\r\n";
    boundBegin += "Content-Type: image/jpeg\r\n";
    boundBegin += "\r\n";

    String boundEnd = "\r\n--ESP32CAM--\r\n";

    uint32_t imgSize = fb->len;  // 取得影像檔的大小
    uint32_t payloadSize = boundBegin.length() + imgSize + boundEnd.length();

    String httpMsg = String("POST ") + UPLOAD_URL + " HTTP/1.1\r\n";
    httpMsg += String("Host: ") + SERVER + "\r\n";
    httpMsg += "User-Agent: Arduino/ESP32CAM\r\n";
    httpMsg += "Content-Length: " + String(payloadSize) + "\r\n";
    httpMsg += "Content-Type: multipart/form-data; boundary=ESP32CAM\r\n";
    httpMsg += "\r\n";
    httpMsg += boundBegin;

    // 送出HTTP標頭訊息
    client.print(httpMsg.c_str());

    // 上傳檔案
    uint8_t *buf = fb->buf;

    for (uint32_t i=0; i<imgSize; i+=1024) {
      if (i+1024 < imgSize) {
        client.write(buf, 1024);
        buf += 1024;
      } else if (imgSize%1024>0) {
        uint32_t remainder = imgSize%1024;
        client.write(buf, remainder);
      }
    }

    client.print(boundEnd.c_str());

    esp_camera_fb_return(fb);

    // 等待伺服器的回應（10秒）
    long timout = 10000L + millis();

    while (timout > millis()) {
      Serial.print(".");
      delay(100);

      if (client.available()){
        // 讀取伺服器的回應
        Serial.println("\n伺服器回應：");
        String line = client.readStringUntil('\r');
        Serial.println(line);
        break;
      }
    }

    Serial.println("關閉連線");
  } else {
    Serial.printf("無法連接伺服器：%s\n", SERVER);
  }

  client.stop();  // 關閉用戶端
}


void loop() {
  // Do nothing. Everything is done in another task by the web server
  Serial.println("take picture") ;
  postImage() ;
  delay(3000);
}
