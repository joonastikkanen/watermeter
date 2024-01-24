// PRE NUMBER ROI'S
var preRoiCount = document.body.getAttribute('data-prerois');
document.getElementById('add-pre-roi').addEventListener('click', function() {
    preRoiCount++;
    var preRoiField = document.createElement('div');
    preRoiField.innerHTML = `
        <label for="preroi_${preRoiCount}">NUMBER ${preRoiCount}:</label><br>
        <input type="text" id="preroi_${preRoiCount}_x" name="preroi_${preRoiCount}_x" size="8" placeholder="X Position">
        <input type="text" id="preroi_${preRoiCount}_y" name="preroi_${preRoiCount}_y" size="8" placeholder="Y Position">
        <input type="text" id="preroi_${preRoiCount}_w" name="preroi_${preRoiCount}_w" size="8" placeholder="Width">
        <input type="text" id="preroi_${preRoiCount}_h" name="preroi_${preRoiCount}_h" size="8" placeholder="Height"><br>
    `;
    preRoiField.id = `preroi_${preRoiCount}`;
    document.getElementById('pre-roi-fields').appendChild(preRoiField);
});

document.getElementById('remove-pre-roi').addEventListener('click', function() {
    if (preRoiCount > 0) {
        var preRoiField = document.getElementById(`preroi_${preRoiCount}`);
        preRoiField.parentNode.removeChild(preRoiField);
        preRoiCount--;
    }
});

// PRE GAUGE ROIS
var preGaugeRoiCount = document.body.getAttribute('data-pregaugerois');
document.getElementById('add-pre-gauge-roi').addEventListener('click', function() {
    preGaugeRoiCount++;
    var preGaugeRoiField = document.createElement('div');
    preGaugeRoiField.innerHTML = `
        <label for="pregaugeroi_${preGaugeRoiCount}">GAUGE ${preGaugeRoiCount}:</label><br>
        <input type="text" id="pregaugeroi_${preGaugeRoiCount}_x" name="pregaugeroi_${preGaugeRoiCount}_x" size="8" placeholder="X Position">
        <input type="text" id="pregaugeroi_${preGaugeRoiCount}_y" name="pregaugeroi_${preGaugeRoiCount}_y" size="8" placeholder="Y Position">
        <input type="text" id="pregaugeroi_${preGaugeRoiCount}_w" name="pregaugeroi_${preGaugeRoiCount}_w" size="8" placeholder="Width">
        <input type="text" id="pregaugeroi_${preGaugeRoiCount}_h" name="pregaugeroi_${preGaugeRoiCount}_h" size="8" placeholder="Height"><br>
    `;
    preGaugeRoiField.id = `pregaugeroi_${preGaugeRoiCount}`;
    document.getElementById('pre-gauge-roi-fields').appendChild(preGaugeRoiField);
});

document.getElementById('remove-pre-gauge-roi').addEventListener('click', function() {
    if (preGaugeRoiCount > 0) {
        var preGaugeRoiField = document.getElementById(`pregaugeroi_${preGaugeRoiCount}`);
        preGaugeRoiField.parentNode.removeChild(preGaugeRoiField);
        preGaugeRoiCount--;
    }
});

// POST NUMBER ROI'S
var postRoiCount = document.body.getAttribute('data-postrois');
document.getElementById('add-post-roi').addEventListener('click', function() {
    postRoiCount++;
    var postRoiField = document.createElement('div');
    postRoiField.innerHTML = `
        <label for="postroi_${postRoiCount}">AREA ${postRoiCount}:</label><br>
        <input type="text" id="postroi_${postRoiCount}_x" name="postroi_${postRoiCount}_x" size="8" placeholder="X Position">
        <input type="text" id="postroi_${postRoiCount}_y" name="postroi_${postRoiCount}_y" size="8" placeholder="Y Position">
        <input type="text" id="postroi_${postRoiCount}_w" name="postroi_${postRoiCount}_w" size="8" placeholder="Width">
        <input type="text" id="postroi_${postRoiCount}_h" name="postroi_${postRoiCount}_h" size="8" placeholder="Height"><br>
    `;
    postRoiField.id = `postroi_${postRoiCount}`;
    document.getElementById('post-roi-fields').appendChild(postRoiField);
});

document.getElementById('remove-post-roi').addEventListener('click', function() {
    if (postRoiCount > 0) {
        var postRoiField = document.getElementById(`postroi_${postRoiCount}`);
        postRoiField.parentNode.removeChild(postRoiField);
        postRoiCount--;
    }
});

// POST GAUGE ROIS
var postGaugeRoiCount = document.body.getAttribute('data-postgaugerois');
document.getElementById('add-post-gauge-roi').addEventListener('click', function() {
    postGaugeRoiCount++;
    var postGaugeRoiField = document.createElement('div');
    postGaugeRoiField.innerHTML = `
        <label for="postgaugeroi_${postGaugeRoiCount}">GAUGE ${postGaugeRoiCount}:</label><br>
        <input type="text" id="postgaugeroi_${postGaugeRoiCount}_x" name="postgaugeroi_${postGaugeRoiCount}_x" size="8" placeholder="X Position">
        <input type="text" id="postgaugeroi_${postGaugeRoiCount}_y" name="postgaugeroi_${postGaugeRoiCount}_y" size="8" placeholder="Y Position">
        <input type="text" id="postgaugeroi_${postGaugeRoiCount}_w" name="postgaugeroi_${postGaugeRoiCount}_w" size="8" placeholder="Width">
        <input type="text" id="postgaugeroi_${postGaugeRoiCount}_h" name="postgaugeroi_${postGaugeRoiCount}_h" size="8" placeholder="Height"><br>
    `;
    postGaugeRoiField.id = `postgaugeroi_${postGaugeRoiCount}`;
    document.getElementById('post-gauge-roi-fields').appendChild(postGaugeRoiField);
});

document.getElementById('remove-post-gauge-roi').addEventListener('click', function() {
    if (postGaugeRoiCount > 0) {
        var postGaugeRoiField = document.getElementById(`postgaugeroi_${postGaugeRoiCount}`);
        postGaugeRoiField.parentNode.removeChild(postGaugeRoiField);
        postGaugeRoiCount--;
    }
});

// LED BRIGHTNESS
const ledValue = document.querySelector("#picamera_led_brightness_value");
const ledInput = document.querySelector("#picamera_led_brightness");
ledValue.textContent = ledInput.value;
ledInput.addEventListener("input", (event) => {
ledValue.textContent = event.target.value;
});

// IMAGE BRIGHTNESS
const brightnessValue = document.querySelector("#picamera_image_brightness_value");
const brightnessInput = document.querySelector("#picamera_image_brightness");
brightnessValue.textContent = brightnessInput.value;
brightnessInput.addEventListener("input", (event) => {
brightnessValue.textContent = event.target.value;
});

// IMAGE CONTRAST
const contrastValue = document.querySelector("#picamera_image_contrast_value");
const contrastInput = document.querySelector("#picamera_image_contrast");
contrastValue.textContent = contrastInput.value;
contrastInput.addEventListener("input", (event) => {
contrastValue.textContent = event.target.value;
});