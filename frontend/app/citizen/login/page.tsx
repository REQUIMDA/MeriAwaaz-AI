import Header from "@/components/layout/Header";
import Hero from "@/components/landing/Hero";
import Footer from "@/components/layout/Footer";

export default function Home() {
  return (
    <main className="min-h-screen bg-[#f7f9fc]">
      <Header />
      <Hero />
      <Footer />
    </main>
  );
}