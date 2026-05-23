import React from "react";
import { Image } from "@heroui/react";
import { useLocalMediaUrl } from "@hooks/useLocalMediaUrl";

type LocalMediaImageProps = Omit<React.ComponentProps<typeof Image>, "src"> & {
  src?: string | null;
};

export const LocalMediaImage: React.FC<LocalMediaImageProps> = ({
  src,
  alt,
  ...props
}) => {
  const { resolvedSrc } = useLocalMediaUrl(src);

  if (!resolvedSrc) return null;

  return <Image src={resolvedSrc} alt={alt} {...props} />;
};
