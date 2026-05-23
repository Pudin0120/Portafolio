import React from "react";
import { Modal, ModalContent } from "@heroui/react";
import { useSidebar } from "@/context/SidebarContext";
import { useIsMobile } from "@/hooks/useIsMobile";

type BaseModalProps = React.ComponentProps<typeof Modal>;

interface CenteredModalProps extends Omit<BaseModalProps, "children"> {
  children: (onClose: () => void) => React.ReactNode;
  onClose?: () => void;
}

export const CenteredModal: React.FC<CenteredModalProps> = ({
  isOpen,
  onOpenChange,
  onClose,
  children,
  ...props
}) => {
  const { isOpen: sidebarOpen } = useSidebar();
  const isMobile = useIsMobile();
  const wrapperPaddingClass =
    !isMobile && sidebarOpen ? "md:pl-[260px]" : "";
  const mergedClassNames = {
    ...props.classNames,
    wrapper: `modal-centered-wrapper flex min-h-dvh items-center justify-center px-2 py-4 sm:px-4 ${wrapperPaddingClass} ${props.classNames?.wrapper ?? ""}`.trim(),
    base: `modal-centered-content mx-0 w-full max-h-[calc(100dvh-2rem)] text-foreground ${props.classNames?.base ?? ""}`.trim(),
    backdrop: `bg-black/70 backdrop-blur-md dark:bg-black/80 ${props.classNames?.backdrop ?? ""}`.trim(),
  };

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      onClose?.();
    }

    onOpenChange?.(open);
  };

  return (
    <Modal
      isOpen={isOpen}
      onOpenChange={handleOpenChange}
      {...props}
      classNames={mergedClassNames}
    >
      <ModalContent>{(onCloseHandler: () => void) => children(onCloseHandler)}</ModalContent>
    </Modal>
  );
};
