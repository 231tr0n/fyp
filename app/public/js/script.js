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
	const sample_size = 10;
	let counter = 0;
	let json = {};
	let bool = false;
	const questions = ['Name', 'Year of birth', 'Gender', 'Id Number'];
	let question_index = 0;
	const answers = {};

	const text_predict = () => {
		if (question_index >= questions.length) {
			document.getElementById('chat').innerHTML += `<div style = 'float: left;'><div style = "border-radius: 10px; width: 300px; height: auto; background-color: #293e49; padding: 10px; color: white;">${JSON.stringify(answers, null, 4)}</div></div>`;
		} else {
			document.getElementById('predicted-text').innerText = '';
			document.getElementById('chat').innerHTML += `<div style = 'float: left;'><div style = "border-radius: 10px; width: 300px; height: auto; background-color: #293e49; padding: 10px; color: white;">Enter ${questions[question_index]}</div></div>`;
			question_index += 1;
			counter = 0;
			json = {};
			bool = true;
		}
	};
	text_predict();

	document.getElementById('submit-output').onclick = () => {
		bool = false;
		const text = document.getElementById('predicted-text').innerText;
		// let temp = '';
		// let t = '';
		// for (let i = 0; i < text.length; i ++) {
		// if (text[i] != t) {
		// t = text[i];
		// temp += text[i];
		// }
		// }
		answers[questions[question_index - 1]] = text;
		document.getElementById('chat').innerHTML += `<div style = 'float: right;'><p style = "border-radius: 10px; width: 300px; height: auto; background-color: #2e7690; padding: 10px; color: white;">${text}</p></div>`;
		text_predict();
		// fetch('/spellcheck', {
		// method: 'POST',
		// mode: 'same-origin',
		// credentials: 'same-origin',
		// body: temp
		// }).then((res) => res.text()).then((res) => {
		// document.getElementById('final-text').innerText = res.toUpperCase();
		// }).catch((error) => {
		// console.log(error);
		// alert('Fetch request failed. Press this button to reload.');
		// location.reload();
		// });
	};

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
			if (res.includes('Right Hand')) {
				calibrator.color_right('#0b171e');
			} else {
				calibrator.color_right('#2e7690');
			}
			if (res.includes('Left Hand')) {
				calibrator.color_left('#0b171e');
			} else {
				calibrator.color_left('#2e7690');
			}
			let answer = res.split(', ');
			answer = answer[answer.length - 1];
			if (answer.length == 1) {
				document.getElementById('prediction').innerText = answer;
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
			upload_delay: 100,
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
