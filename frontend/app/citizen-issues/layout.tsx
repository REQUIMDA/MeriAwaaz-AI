import Sidebar from "@/components/mp/Sidebar";
import VoiceFAB from "@/components/mp/VoiceFAB";

export default function CitizenIssuesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[#F7F9FC]">
      <Sidebar />

      <main className="ml-[280px] p-8">
        {children}
      </main>

      <VoiceFAB />
    </div>
  );
}