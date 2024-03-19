// Define an array of input elements and their corresponding value elements
/**
 * Array of elements containing input and value selectors.
 * @type {Array<{input: string, value: string}>}
 */
const elements = [
    { input: "#picamera_led_brightness", value: "#picamera_led_brightness_value" },
    { input: "#picamera_image_brightness", value: "#picamera_image_brightness_value" },
    { input: "#picamera_image_contrast", value: "#picamera_image_contrast_value" },
    { input: "#picamera_image_sharpness", value: "#picamera_image_sharpness_value" },
    { input: "#picamera_image_focus_position", value: "#picamera_image_focus_position_value" }
];

// Attach event listeners to each input element
elements.forEach(({ input, value }) => {
    const inputElement = document.querySelector(input);
    const valueElement = document.querySelector(value);
    valueElement.textContent = inputElement.value;
    inputElement.addEventListener("input", (event) => {
        valueElement.textContent = event.target.value;
    });
});
