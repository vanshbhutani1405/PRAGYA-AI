import { useState } from "react";
import { Share2 } from "lucide-react";
import { useGraph, useNodeDetail } from "../hooks/useGraph";
import {
  GraphCanvas,
  GraphLegend,
  NodeDetailPanel,
} from "../components/graph/GraphCanvas";
import { PageContainer, PageHeader } from "../components/ui/PageHeader";
import { Skeleton } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { ErrorState } from "../components/ui/ErrorState";

export function GraphExplorer() {
  const [selected, setSelected] = useState<string | null>(null);
  const { data, isLoading, isError, refetch } = useGraph();
  const detail = useNodeDetail(selected);

  return (
    <PageContainer>
      <PageHeader
        title="Graph Explorer"
        subtitle="The connected knowledge graph of equipment, permits and regulatory entities."
        actions={<GraphLegend />}
      />

      <div className="mt-6">
        {isLoading ? (
          <Skeleton className="h-[560px] w-full" />
        ) : isError ? (
          <ErrorState
            message="Failed to load the knowledge graph."
            onRetry={() => refetch()}
          />
        ) : !data || data.nodes.length === 0 ? (
          <EmptyState
            icon={Share2}
            title="Graph is empty"
            message="No entities have been ingested yet. Upload documents to build the knowledge graph."
          />
        ) : (
          <div className="flex flex-col gap-6 lg:flex-row">
            <div className="min-h-[480px] flex-1 overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
              <GraphCanvas
                data={data}
                selected={selected}
                onSelect={setSelected}
              />
            </div>
            {selected && (
              <NodeDetailPanel
                detail={detail.data}
                loading={detail.isLoading}
                onClose={() => setSelected(null)}
              />
            )}
          </div>
        )}
      </div>
    </PageContainer>
  );
}
