const canvas = function (element_id, width, height) {
	const drawer = document.getElementById(element_id);
	drawer.width = width;
	drawer.height = height;
	const pencil = drawer.getContext('2d');
	this.draw_image = (video_object) => {
		pencil.drawImage(video_object, 0, 0, width, height);
	};
	this.data_url = () => drawer.toDataURL();
	this.blob_converter = () => new Promise((resolve, reject) => {
		drawer.toBlob((blob_data) => {
			if (blob_data != null) {
				resolve(blob_data);
			} else {
				reject(new Error('Blob data error.'));
			}
		}, 'image/jpg');
	});
};

const mediapipe = function (cb) {
	this.onprediction = cb;
	this.predict = (recorded_video_blob) => {
		const fd = new FormData();
		fd.append('image', new File([recorded_video_blob], 'image.jpg'));
		fetch('/calibrate', {
			method: 'POST',
			mode: 'same-origin',
			credentials: 'same-origin',
			body: fd
		}).then((res) => res.text()).then((res) => {
			this.onprediction(res);
		}).catch((error) => {
			console.log(error);
			alert('Fetch request failed. Press this button to reload.');
			location.reload();
		});
	};
};

const video_calibrator = function (element_id, width, height, actual_stream) {
	const video = document.getElementById(element_id);
	video.style.transform = 'scale(-1, 1)';
	video.style.width = width;
	video.style.height = height;
	video.srcObject = actual_stream;
	video.loop = false;

	this.color_left = (color) => {
		video.style.borderLeftColor = color;
	};
	this.color_right = (color) => {
		video.style.borderRightColor = color;
	};
	this.color_top = (color) => {
		video.style.borderTopColor = color;
	};
	this.color_bottom = (color) => {
		video.style.borderBottomColor = color;
	};
	this.get_video = () => video;
};

const chatbot = function (params) {
	const canvas_id = params.canvas_id;
	const video_id = params.video_id;
	const video_width = params.video_width;
	const video_height = params.video_height;
	const video_style_width = params.video_style_width;
	const video_style_height = params.video_style_height;
	const upload_delay = params.upload_delay;
	const video_stream = params.video_stream;

	let reply = true;
	let interval = null;
	const sample_size = 12;
	let counter = 0;
	let json = {};
	let bool = false;
	let swap = true;

	const text_predict = () => {
		document.getElementById('predicted-text').innerText = '';
		document.getElementById('final-text').innerText = '';
		counter = 0;
		json = {};
		bool = true;
	};

	document.getElementById('swap').onclick = () => {
		if (swap) {
			document.getElementById('swap').innerText = 'Select Options';
			document.getElementById('enter-text').hidden = false;
			document.getElementById('select-option').hidden = true;
			swap = false;
			text_predict();
		} else {
			bool = false;
			document.getElementById('swap').innerText = 'Enter Text';
			document.getElementById('enter-text').hidden = true;
			document.getElementById('select-option').hidden = false;
			swap = true;
		}
	};

	document.getElementById('submit-output').onclick = () => {
		bool = false;
		const text = document.getElementById('predicted-text').innerText;
		let temp = '';
		let t = '';
		for (let i = 0; i < text.length; i ++) {
			if (text[i] != t) {
				t = text[i];
				temp += text[i];
			}
		}
		fetch('/spellcheck', {
			method: 'POST',
			mode: 'same-origin',
			credentials: 'same-origin',
			body: temp
		}).then((res) => res.text()).then((res) => {
			document.getElementById('final-text').innerText = res.toUpperCase();
		}).catch((error) => {
			console.log(error);
			alert('Fetch request failed. Press this button to reload.');
			location.reload();
		});
	};

	const prediction_box = document.getElementById(params.prediction_box);
	const tick_img = document.getElementById(params.tick_img);
	const left_img = document.getElementById(params.left_img);
	const right_img = document.getElementById(params.right_img);
	const face_img = document.getElementById(params.face_img);

	const imager = new canvas(canvas_id, video_width, video_height);
	const calibrator = new video_calibrator(video_id, video_style_width, video_style_height, video_stream);

	this.start_frame_upload = (mlpipe) => {
		interval = setInterval(() => {
			if (reply) {
				reply = false;
				imager.draw_image(calibrator.get_video());
				imager.blob_converter().then((blob_data) => {
					mlpipe.predict(blob_data);
				});
			}
		}, upload_delay);
	};

	this.stop_frame_upload = () => {
		clearInterval(interval);
	};

	const mlpipe = new mediapipe((res) => {
		reply = true;
		if (res.includes('Error')) {
			alert('Internal Error. Press this button to reload.');
			location.reload();
		} else {
			if (res.includes('Face')) {
				face_img.hidden = false;
			} else {
				face_img.hidden = true;
			}
			if (res.includes('Right Hand')) {
				left_img.hidden = false;
			} else {
				left_img.hidden = true;
			}
			if (res.includes('Left Hand')) {
				right_img.hidden = false;
			} else {
				right_img.hidden = true;
			}
			if (!res.includes('Face') && !res.includes('Right Hand') && !res.includes('Left Hand')) {
				tick_img.hidden = false;
			} else {
				tick_img.hidden = true;
			}
			let answer = res.split(', ');
			answer = answer[answer.length - 1];
			const characters = ['1', '2', '3', '4', 'A', 'B', 'C'];
			if (answer.length == 1) {
				prediction_box.innerText = answer;
				if (swap) {
					if (characters.includes(answer)) {
						document.getElementById(`radio${answer}`).checked = true;
					}
				} else {
					if (answer != '_' && bool) {
						if (counter < sample_size) {
							counter += 1;
							if (json[answer]) {
								json[answer] += 1;
							} else {
								json[answer] = 1;
							}
						} else {
							let maximum = 0;
							let index = 0;
							for (const i of Object.keys(json)) {
								if (maximum < json[i]) {
									maximum = json[i];
									index = i;
								}
							}
							document.getElementById('predicted-text').innerText += index;
							counter = 0;
							json = {};
						}
					}
				}
			}
		}
	});
	this.start_frame_upload(mlpipe);
};

window.globals = {};

if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
	navigator.mediaDevices.getUserMedia({
		audio: false,
		video: true
	}).then((stream) => {
		window.globals.chatbot = new chatbot({
			canvas_id: 'drawer',
			video_id: 'video',
			left_img: 'leftimg',
			right_img: 'rightimg',
			face_img: 'faceimg',
			tick_img: 'tickimg',
			video_width: 320,
			video_height: 240,
			video_style_width: '320px',
			video_style_height: '240px',
			upload_delay: 1000,
			video_stream: stream,
			prediction_box: 'prediction'
		});
	}).catch((error) => {
		console.log(error);
		alert('Enable webcam access and press this button to reload.');
		location.reload();
	});
} else {
	alert('Video playback using webcam not supported by the browser. Click this button to reload.');
	location.reload();
}
