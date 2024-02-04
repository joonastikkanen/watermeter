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

// IMAGE SHARPNESS
var sharpnessValue = document.querySelector("#picamera_image_sharpness_value");
var sharpnessInput = document.querySelector("#picamera_image_sharpness");
sharpnessValue.textContent = sharpnessInput.value;
sharpnessInput.addEventListener("input", (event) => {
sharpnessValue.textContent = event.target.value;
});

// IMAGE FOCUS
var focusValue = document.querySelector("#picamera_image_focus_position_value");
var focusInput = document.querySelector("#picamera_image_focus_position");
focusValue.textContent = focusInput.value;
focusInput.addEventListener("input", (event) => {
focusValue.textContent = event.target.value;
});
