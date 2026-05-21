import { DashboardShell } from "@/components/dashboard-shell";

export default function DelegatePage({ params }: { params: { id: string } }) {
  return <DashboardShell initialDelegateId={params.id} />;
}

