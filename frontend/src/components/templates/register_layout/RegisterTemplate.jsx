export default function RegisterTemplate({ children }) {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-border px-4 sm:px-6 md:px-8">
      <div className="w-full max-w-md lg:max-w-lg xl:max-w-xl">{children}</div>
    </main>
  );
}
