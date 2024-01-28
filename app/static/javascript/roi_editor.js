var canvas = document.getElementById('canvas');
var ctx = canvas.getContext('2d');
var rect = {};
var rois = [];
var drag = false;
var id = "{{ roi_id }}";

function init() {
    canvas.addEventListener('mousedown', mouseDown, false);
    canvas.addEventListener('mouseup', mouseUp, false);
    canvas.addEventListener('mousemove', mouseMove, false);
}

function mouseDown(e) {
    rect.startX = e.pageX - this.offsetLeft;
    rect.startY = e.pageY - this.offsetTop;
    drag = true;
}

function mouseUp() {
    drag = false;
    rois.push({
        id: 'preroi_' + (rois.length + 1),
        x: rect.startX,
        y: rect.startY,
        w: rect.w,
        h: rect.h
    });
    rect = {};
}

function mouseMove(e) {
    if (drag) {
        rect.w = (e.pageX - this.offsetLeft) - rect.startX;
        rect.h = (e.pageY - this.offsetTop) - rect.startY;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        draw();
    }
}

function draw() {
    rois.forEach(function(roi) {
        ctx.strokeRect(roi.x, roi.y, roi.w, roi.h);
    });
    if (drag) {
        ctx.strokeRect(rect.startX, rect.startY, rect.w, rect.h);
    }
}

init();
document.getElementById('{{ roi_name }}').addEventListener('submit', function(e) {
    var roisTuples = rois.flatMap(function(roi) {
        return [
            [roi.id + '_x', roi.x],
            [roi.id + '_y', roi.y],
            [roi.id + '_w', roi.w],
            [roi.id + '_h', roi.h]
        ];
    });
    document.getElementById('{{ roi_id }}').value = JSON.stringify(roisTuples);
    e.preventDefault();
});
