export const getOfflineBannerContainerClassName = (
	isMobile: boolean,
	isMenuOpen: boolean,
): string => {
	if (isMobile) {
		return "fixed inset-x-3 top-3 z-[60]";
	}

	return `fixed top-3 z-[60] ${
		isMenuOpen ? "left-[276px] right-3" : "left-3 right-3"
	}`;
};
