import { useEffect, useState } from "react";
import { getLocalMedia, isLocalMediaUrl } from "@services/localMediaStore";

export const useLocalMediaUrl = (src?: string | null) => {
  const [resolvedSrc, setResolvedSrc] = useState(src || "");
  const [isResolving, setIsResolving] = useState(false);

  useEffect(() => {
    let objectUrl = "";
    let isMounted = true;

    const resolve = async () => {
      if (!src) {
        setResolvedSrc("");
        return;
      }

      if (!isLocalMediaUrl(src)) {
        setResolvedSrc(src);
        return;
      }

      setIsResolving(true);
      try {
        const record = await getLocalMedia(src);
        if (!record || !isMounted) return;

        objectUrl = URL.createObjectURL(record.blob);
        setResolvedSrc(objectUrl);
      } finally {
        if (isMounted) setIsResolving(false);
      }
    };

    resolve();

    return () => {
      isMounted = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [src]);

  return { resolvedSrc, isResolving, isLocal: isLocalMediaUrl(src) };
};
