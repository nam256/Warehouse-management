import { useEffect, useState } from "react";

type Props = {
  src?: string | null;
  alt?: string;
  label?: string;
  size?: "sm" | "md";
  className?: string;
};

export default function ProductThumb({ src, alt = "", label, size = "sm", className }: Props) {
  const [broken, setBroken] = useState(false);
  const initial = (label || alt || "?").trim().charAt(0).toLocaleUpperCase("vi");

  useEffect(() => {
    setBroken(false);
  }, [src]);

  const showImg = Boolean(src) && !broken;

  return (
    <span className={`product-thumb product-thumb--${size}${className ? ` ${className}` : ""}`} aria-hidden={!alt}>
      {showImg ? (
        <img src={src!} alt={alt} loading="lazy" onError={() => setBroken(true)} />
      ) : (
        <span className="product-thumb__fallback">{initial}</span>
      )}
    </span>
  );
}
