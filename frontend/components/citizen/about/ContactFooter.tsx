import {
  Landmark,
  Globe,
  HelpCircle,
  Scale,
  Share2,
} from "lucide-react";

export default function ContactFooter() {
  return (
    <footer className="border-t border-[#c3c7cc]/30 px-6 pb-16 pt-24">

      <div className="mx-auto max-w-7xl">

        <div className="grid gap-12 md:grid-cols-4">

          {/* Brand */}

          <div>

            <div className="mb-5 flex items-center gap-3">

              <Landmark
                size={28}
                className="text-black"
              />

              <h2 className="text-2xl font-bold">
                MeriAwaaz AI
              </h2>

            </div>

            <p className="mb-6 leading-7 text-[#43474b]">
              An initiative by the Ministry of Electronics and
              Information Technology (MeitY) under the Digital India
              programme.
            </p>

            <div className="flex gap-4">

              <img
                src="/images/digital-india.png"
                alt="Digital India"
                className="h-10 opacity-60 grayscale transition hover:grayscale-0"
              />

              <img
                src="/images/emblem.png"
                alt="Government of India"
                className="h-10 opacity-60 grayscale transition hover:grayscale-0"
              />

            </div>

          </div>

          {/* Connect */}

          <div>

            <h3 className="mb-5 text-sm font-semibold uppercase tracking-[0.25em]">
              Connect
            </h3>

            <ul className="space-y-3 text-[#43474b]">

              <li>
                <a href="#">Help Center</a>
              </li>

              <li>
                <a href="#">Grievance Officer</a>
              </li>

              <li>
                <a href="#">Media Kit</a>
              </li>

            </ul>

          </div>

          {/* Legal */}

          <div>

            <h3 className="mb-5 text-sm font-semibold uppercase tracking-[0.25em]">
              Legal
            </h3>

            <ul className="space-y-3 text-[#43474b]">

              <li>
                <a href="#">Privacy Policy</a>
              </li>

              <li>
                <a href="#">Terms of Service</a>
              </li>

              <li>
                <a href="#">AI Ethics Charter</a>
              </li>

            </ul>

          </div>

          {/* Digital India */}

          <div>

            <h3 className="mb-5 text-sm font-semibold uppercase tracking-[0.25em]">
              Digital India
            </h3>

            <ul className="space-y-3 text-[#43474b]">

              <li>
                <a href="#">MyGov.in</a>
              </li>

              <li>
                <a href="#">India.gov.in</a>
              </li>

              <li>
                <a href="#">Digital India Week</a>
              </li>

            </ul>

          </div>

        </div>

        {/* Bottom */}

        <div className="mt-20 flex flex-col items-center justify-between gap-6 border-t border-[#c3c7cc]/30 pt-8 md:flex-row">

          <p className="text-sm text-[#43474b]">
            © 2024 MeriAwaaz AI. National Informatics Centre. All rights
            reserved.
          </p>

          <div className="flex gap-6">

            <button className="transition hover:scale-110">
              <HelpCircle size={20} />
            </button>

            <button className="transition hover:scale-110">
              <Share2 size={20} />
            </button>

            <button className="transition hover:scale-110">
              <Globe size={20} />
            </button>

          </div>

        </div>

      </div>

    </footer>
  );
}