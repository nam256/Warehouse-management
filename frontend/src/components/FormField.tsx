
type Props = {
  label: string;
  children: React.ReactNode;
};

export default function FormField({ label, children }: Props) {
  return (
    <label>
      {label}
      {children}
    </label>
  );
}
