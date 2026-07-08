import Navbar from "@/components/citizen/Navbar";
import Hero from "@/components/citizen/Hero";
import Stats from "@/components/citizen/Stats";
import HowItWorks from "@/components/citizen/HowItWorks";
import Privacy from "@/components/citizen/Privacy";
import Footer from "@/components/citizen/Footer";
import BottomNav from "@/components/citizen/BottomNav";

export default function CitizenHome() {
  return (
    <>
      <Navbar />

      <main className="bg-[#f7f9fc]">
        <Hero />
        <Stats />
        <HowItWorks />
        <Privacy />
        <Footer />
      </main>

      <BottomNav />
    </>
  );
}