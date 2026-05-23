import React, { useEffect, useState } from "react";
import { Menu } from "lucide-react";
import { SidebarMenu, type MenuItem } from "./SidebarMenu";
import { Breadcrumbs, type BreadcrumbItem } from "./Breadcrumbs";
import { UserProfileMenu } from "./UserProfileMenu";
import { NetworkStatusIndicator } from "@components/common/NetworkStatusIndicator";
import { useSidebar } from "@/context/SidebarContext";
import { useIsMobile } from "@/hooks/useIsMobile";
import { OfflineBanner } from "@/components/offline/OfflineBanner";
import { getOfflineBannerContainerClassName } from "@/components/offline/offlineBannerLayout";
import { SyncQueuePanel } from "@/components/sync/SyncQueuePanel";

interface DashboardLayoutProps {
	children: React.ReactNode;
	menuItems: MenuItem[];
	breadcrumbItems: BreadcrumbItem[];
	isModalOpen?: boolean;
	onMenuToggle: () => void;
	onMenuItemClick: (key: string) => void;
	onBreadcrumbClick: (key: string) => void;
	onLogout: () => void;
	userProfile?: {
		first_name: string;
		last_name: string;
		email: string;
	} | null;
	userEmail?: string | null;
	onMenuStateChange?: (isOpen: boolean) => void;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
	children,
	menuItems,
	breadcrumbItems,
	onMenuToggle,
	onMenuItemClick,
	onBreadcrumbClick,
	onLogout,
	userProfile,
	userEmail,
	onMenuStateChange,
	isModalOpen = false,
}) => {
	const isMobile = useIsMobile();
	const [isDesktopMenuOpen, setIsDesktopMenuOpen] = useState(true);
	const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
	const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
	const [isSyncQueueOpen, setIsSyncQueueOpen] = useState(false);
	const { setIsOpen: setSidebarOpen } = useSidebar();
	const isMenuOpen = isMobile ? isMobileMenuOpen : isDesktopMenuOpen;

	useEffect(() => {
		setSidebarOpen(isMenuOpen);
	}, [isMenuOpen, setSidebarOpen]);

	useEffect(() => {
		onMenuStateChange?.(isMenuOpen);
	}, [isMenuOpen, onMenuStateChange]);

	useEffect(() => {
		const handleClickOutside = (event: MouseEvent) => {
			const target = event.target as Element;
			if (isProfileMenuOpen && !target.closest("[data-profile-menu]")) {
				setIsProfileMenuOpen(false);
			}
		};

		document.addEventListener("mousedown", handleClickOutside);
		return () => document.removeEventListener("mousedown", handleClickOutside);
	}, [isProfileMenuOpen]);

	const handleMenuToggle = () => {
		if (isMobile) {
			setIsMobileMenuOpen((prev) => !prev);
		} else {
			setIsDesktopMenuOpen((prev) => !prev);
		}
		onMenuToggle();
	};

	const handleMenuClose = () => {
		if (isMobile) {
			setIsMobileMenuOpen(false);
		} else {
			setIsDesktopMenuOpen(false);
		}
	};

	const handleMenuItemClick = (key: string) => {
		onMenuItemClick(key);
		if (isMobile) {
			setIsMobileMenuOpen(false);
		}
	};

	const handleProfileToggle = () => setIsProfileMenuOpen((prev) => !prev);

	return (
		<>
			<div className={getOfflineBannerContainerClassName(isMobile, isMenuOpen)}>
				<OfflineBanner onOpenSyncQueue={() => setIsSyncQueueOpen(true)} />
			</div>
			<div className="flex min-h-dvh overflow-x-hidden bg-background text-foreground transition-colors duration-300 dark:bg-background">
				{isMobile && isMenuOpen && (
					<button
						type="button"
						aria-label="Cerrar menu"
						className="fixed inset-0 z-[998] border-0 bg-black/50 p-0 transition-opacity"
						onClick={handleMenuClose}
					/>
				)}

				<SidebarMenu
					isOpen={isMenuOpen}
					onClose={handleMenuClose}
					menuItems={menuItems}
					onItemClick={handleMenuItemClick}
					isMobile={isMobile}
					className={`transition-all duration-300 ${
						isModalOpen ? "pointer-events-none blur-sm" : ""
					}`}
				/>

				<div
					id="main-content"
					className={`flex min-w-0 flex-1 flex-col overflow-x-hidden transition-[margin] duration-300 ease-in-out ${
						!isMobile && isMenuOpen ? "md:ml-[260px]" : "ml-0"
					}`}
				>
					<header
						className={`sticky top-0 z-40 border-b border-surface-border bg-surface-elevated/98 shadow-sm backdrop-blur-md ${
							isMobile ? "px-3 py-2" : "px-4 py-4 md:px-6"
						}`}
					>
						{isMobile ? (
							<div className="flex flex-col gap-2">
								<div className="flex items-center justify-between">
									<button
										type="button"
										onClick={handleMenuToggle}
										className="flex shrink-0 items-center justify-center rounded-md p-2 transition-colors hover:bg-surface-hover focus:outline-hidden"
									>
										<Menu className="h-6 w-6" />
									</button>

									<div className="flex items-center gap-4">
										<NetworkStatusIndicator />
										<div className="h-5 w-px bg-divider" />
										<UserProfileMenu
											isOpen={isProfileMenuOpen}
											onToggle={handleProfileToggle}
											onLogout={onLogout}
											userProfile={userProfile}
											userEmail={userEmail}
										/>
									</div>
								</div>

								<div className="w-full overflow-x-auto pb-1">
									<Breadcrumbs
										items={breadcrumbItems}
										onItemClick={onBreadcrumbClick}
									/>
								</div>
							</div>
						) : (
							<div className="flex items-center justify-between gap-4">
								<div className="flex min-w-0 items-center gap-4">
									<button
										type="button"
										onClick={handleMenuToggle}
										className="flex shrink-0 items-center justify-center rounded-md p-2 transition-colors hover:bg-surface-hover focus:outline-hidden"
									>
										<Menu className="h-6 w-6" />
									</button>

									<div className="min-w-0">
										<Breadcrumbs
											items={breadcrumbItems}
											onItemClick={onBreadcrumbClick}
										/>
									</div>
								</div>

								<div className="flex items-center gap-4">
									<NetworkStatusIndicator showLabel />
									<div className="h-5 w-px bg-divider" />
									<UserProfileMenu
										isOpen={isProfileMenuOpen}
										onToggle={handleProfileToggle}
										onLogout={onLogout}
										userProfile={userProfile}
										userEmail={userEmail}
									/>
								</div>
							</div>
						)}
					</header>

					<main
						className={`relative flex-1 ${isMobile ? "p-3" : "p-4 md:p-6"}`}
					>
						{children}
					</main>
				</div>
			</div>
			<SyncQueuePanel
				isOpen={isSyncQueueOpen}
				onClose={() => setIsSyncQueueOpen(false)}
			/>
		</>
	);
};
