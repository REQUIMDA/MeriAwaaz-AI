import Navbar from "@/components/citizen/Navbar";
import AboutHero from "../../../components/citizen/about/AboutHero";
import AIWorkflow from "@/components/citizen/about/AIWorkflow";
import PrivacySection from "@/components/citizen/about/PrivacySection";
import FAQ from "@/components/citizen/about/FAQ";
import ContactFooter from "@/components/citizen/about/ContactFooter";
import BottomNav from "@/components/citizen/BottomNav";
import VoiceFAB from "@/components/citizen/VoiceFAB";

export default function AboutPage() {
  return (
    <>
      <Navbar />

      <main className="bg-[#f7f9fc]">
        <AboutHero />
        <AIWorkflow />
        <PrivacySection />
        <FAQ />
        <ContactFooter />
      </main>

      <VoiceFAB />
      <BottomNav />
    </>
  );
}