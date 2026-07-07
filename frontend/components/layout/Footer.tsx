export default function Footer() {
  return (
    <footer className="mt-auto border-t border-[#c3c7cc]/20 bg-[#f2f4f7]/50 py-8">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-6 px-6 md:flex-row">
        <div className="flex items-center gap-4">
          <div className="hidden text-right md:block">
            <p className="text-sm font-medium text-black">
              Ministry of Electronics & IT
            </p>

            <p className="text-[10px] text-[#43474b]">
              Government of India Initiative
            </p>
          </div>

          <div className="hidden h-8 w-px bg-[#c3c7cc] md:block" />

          <p className="max-w-xs text-center text-[11px] text-[#43474b] md:text-left">
            Official Secure Access. Encrypted with 256-bit SSL.
            © 2024 National Informatics Centre.
          </p>
        </div>

        <div className="flex gap-6 text-sm text-[#43474b]">
          <button>Privacy Policy</button>
          <button>Terms of Service</button>
          <button>Contact NIC</button>
        </div>
      </div>
    </footer>
  );
}