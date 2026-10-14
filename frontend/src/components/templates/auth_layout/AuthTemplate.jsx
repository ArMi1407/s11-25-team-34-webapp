export default function AuthTemplate({ children, title }) {
  return (
    <main className="flex items-center justify-center min-h-screen bg-border">
      <div className="w-full max-w-80 sm:max-w-100 md:max-w-md lg:max-w-lg xl:max-w-xl bg-white">
        {children}
      </div>
    </main>
  );
}
