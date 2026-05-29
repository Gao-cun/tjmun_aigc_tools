import { DashboardShell } from "@/components/dashboard-shell";

export default async function DelegatePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <DashboardShell initialDelegateId={id} />;
}
