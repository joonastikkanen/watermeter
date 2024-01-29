// LED BRIGHTNESS
var ledValue = document.querySelector("#picamera_led_brightness_value");
var ledInput = document.querySelector("#picamera_led_brightness");
ledValue.textContent = ledInput.value;
ledInput.addEventListener("input", (event) => {
ledValue.textContent = event.target.value;
});

// IMAGE BRIGHTNESS
var brightnessValue = document.querySelector("#picamera_image_brightness_value");
var brightnessInput = document.querySelector("#picamera_image_brightness");
brightnessValue.textContent = brightnessInput.value;
brightnessInput.addEventListener("input", (event) => {
brightnessValue.textContent = event.target.value;
});

// IMAGE CONTRAST
var contrastValue = document.querySelector("#picamera_image_contrast_value");
var contrastInput = document.querySelector("#picamera_image_contrast");
contrastValue.textContent = contrastInput.value;
contrastInput.addEventListener("input", (event) => {
contrastValue.textContent = event.target.value;
});
