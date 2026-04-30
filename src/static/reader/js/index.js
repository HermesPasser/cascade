"use strict";
// TODO: md has an option to fix the sidebar, which will make it occupy space
//       instead of be on top of the pages 📌
// TODO: dark mode

const DISPLAY_MODE = Object.freeze({
	LONG_STRIP: "longstrip",
	SINGLE_PAGE: "singlepage"
});

const SIZE_MODE = Object.freeze({
	FIT_WIDTH: { value: "fit-width", text: "Fit Width" },
	FIT_HEIGHT: { value: "fit-height", text: "Fit Height" },
	STRETCH_WIDTH: { value: "stretch-width", text: "Stretch Width" },
	NO_LIMIT: { value: "no-limit", text: "No Limit" }
});

let mode = DISPLAY_MODE.SINGLE_PAGE;
let currentSizeMode = SIZE_MODE.FIT_WIDTH;
const images = JSON.parse(imagesJson.textContent);
let index = (Number.parseInt(new URLSearchParams(new URL(window.location).search).get("page")) || 1) - 1;

window.onload = (_) => {
	updateSelector();
	display(mode);
	applySize(SIZE_MODE.FIT_WIDTH);
};

function display(newMode) {
	// TODO: May we should not actually delete all the elements when its not need?
	mode = newMode;
	let maybeImgToScroolTo = null;
	imageWrapper.querySelectorAll("*").forEach((e) => e.remove());
	if (mode === DISPLAY_MODE.LONG_STRIP) {
		layoutLongstrip();
		images.forEach((image, i) => {
			const img = document.createElement("img");
			img.src = image;
			img.setAttribute("data-img-index", i.toString());
			// Maybe add the option for lerping to the next image instead of jumping
			imageWrapper.appendChild(img);

			if (i === index) {
				maybeImgToScroolTo = img;
			}

			if (i === images.length - 1) {
				// NOTE: if i pass the img dimensions, set the size beforehand then i would not have to wait
				//       for others images to load before scrolling into the right place.

				// Scroll to current image index after the last image (and the others, i hope) is loaded
				img.onload = () => {
					if (maybeImgToScroolTo) {
						maybeImgToScroolTo.scrollIntoView();
					}
				};
				img.onerror = img.onload;
			}
		});
	} else {
		layoutManga();
		const img = document.createElement("img");
		img.src = images[index] ?? images[0];
		img.setAttribute("data-img-index", "0");
		imageWrapper.appendChild(img);
	}
}

function toogleMode() {
	if (mode === DISPLAY_MODE.LONG_STRIP) {
		manga();
		modeButton.innerText = "Mode: Single Page";
	} else {
		modeButton.innerText = "Mode: Long Strip";
		longstrip();
	}
}

function toogleSize() {
	const sizingModes = Object.values(SIZE_MODE);
	const index = (sizingModes.indexOf(currentSizeMode) + 1) % sizingModes.length;
	applySize(sizingModes[index]);
}

function applySize(sizeMode) {
	currentSizeMode = sizeMode;
	imageWrapper.className = "image-wrapper " + currentSizeMode.value;
	sizeButton.innerText = "Size: " + currentSizeMode.text;
}

function fullscreen() {
	if (document.fullscreenElement) {
		document.exitFullscreen();
		fullscreenButton.innerText = "Fullscreen: Disabled";
	} else {
		document.body.requestFullscreen();
		fullscreenButton.innerText = "Fullscreen: Enabled";
	}
}

function handleScroll(event) {
	if (mode === DISPLAY_MODE.LONG_STRIP) {
		const element = document.elementFromPoint(event.clientX, event.clientY);

		if (!(element instanceof HTMLImageElement)) {
			return;
		}

		const currentImageIndex = parseInt(element.attributes["data-img-index"].value);
		if (currentImageIndex !== index) {
			index = currentImageIndex;
			updatePageUrl(currentImageIndex);
			updateSelector(currentImageIndex);
		}
	}
}

function handleClick(event) {
	// Would be nice if this was changed to clicking top/bottom on longstrip mode
	// TODO: later configure if 'left' click should go back or if clicking should go always to the next
	const rect = event.target.getBoundingClientRect();
	const x = event.clientX - rect.left;
	const w = rect.width;
	if (x < w / 3) {
		previousImage();
	} else if (x < (2 * w) / 3) {
		controls.classList.toggle("closed");
	} else {
		nextImage();
	}
}

function previousEntry() {
	const current = "{{ current }}";
	const currentEl = Array.from(entrySelector.getElementsByTagName("option")).find((o) => o.value === current);

	if (currentEl.previousElementSibling) {
		changeEntry(currentEl.previousElementSibling.value);
	}
}

function nextEntry() {
	const current = "{{ current }}";
	const currentEl = Array.from(entrySelector.getElementsByTagName("option")).find((o) => o.value === current);

	if (currentEl.nextElementSibling) {
		changeEntry(currentEl.nextElementSibling.value);
	}
}

function changeEntry(entry) {
	window.location.replace("/unzip?file=" + entry);
}

function updateSelector() {
	pageSelector.value = index + 1;
	const percentage = ((index + 1) / images.length) * 100;
	root.style.setProperty("--progress", percentage + "%");
}

function previousImage() {
	changePage(index - 1);
}

function nextImage() {
	changePage(index + 1);
}

function changePageFromSelector() {
	changePage(pageSelector.value - 1);
}

function changePage(newIndex) {
	if (newIndex < 1 || newIndex >= images.length) {
		newIndex = 0;
	}

	index = newIndex;
	// TODO: make option scrolling into view be also "instant"

	if (mode === DISPLAY_MODE.SINGLE_PAGE) {
		const imgElement = imageWrapper.getElementsByTagName("img")[0];
		imgElement.src = images[index];

		// On single page mode we scroll back to the top when the image is replaced by the next
		// TODO: make configurable
		imageWrapper.scrollIntoView({ behavior: "smooth" });
	} else if (mode === DISPLAY_MODE.LONG_STRIP) {
		// TODO: this can make the scroll go backwards if the user is
		//       "between" two pages. To fix we need to get the index
		//       from the image that the user actually clicked
		const imgElement = imageWrapper.querySelector(`[data-img-index="${newIndex}"]`);
		imgElement.scrollIntoView({ behavior: "smooth" });
	}

	updatePageUrl(index);
	updateSelector(index);
}

function updatePageUrl(index) {
	//  The page number on the url is 1-based so we convert the index here
	let url = new URL(window.location.href);
	url.searchParams.set("page", (index + 1).toString());
	window.history.pushState({}, "", url);
}

const root = document.documentElement;
function padding() {
	root.style.setProperty("--img-margin", "20px");
}

function layoutLongstrip() {
	root.style.setProperty("--img-margin", "auto");
	root.style.setProperty("--direction", "column");
}

function longstrip() {
	display(DISPLAY_MODE.LONG_STRIP);
}

function layoutManga() {
	root.style.setProperty("--img-margin", "auto");
	root.style.setProperty("--direction", "row");
}

function manga() {
	display(DISPLAY_MODE.SINGLE_PAGE);
	imageWrapper.scrollIntoView();
}

function toogleProgress() {
	if (progressBar.style.display === "") {
		progressBar.style.display = "none";
		progressButton.innerText = "Progress bar: hidden";
	} else {
		progressBar.style.display = "";
		progressButton.innerText = "Progress bar: visible";
	}
}
