import { useMemo, useEffect } from "react";
import {
	Button,
	Card,
	CardBody,
	Drawer,
	DrawerBody,
	DrawerContent,
	DrawerHeader,
	Table,
	TableBody,
	TableCell,
	TableColumn,
	TableHeader,
	TableRow,
	Tabs,
	Tab,
} from "@heroui/react";
import { useSyncQueue } from "@/hooks/useSyncQueue";
import { SyncBadge } from "@/components/sync/SyncBadge";

interface SyncQueuePanelProps {
	isOpen: boolean;
	onClose: () => void;
}

export function SyncQueuePanel({ isOpen, onClose }: SyncQueuePanelProps) {
	const {
		operations,
		pendingCount,
		errorCount,
		syncedCount,
		isLoading,
		refresh,
	} = useSyncQueue();

	useEffect(() => {
		if (isOpen) {
			void refresh();
		}
	}, [isOpen, refresh]);

	const stats = useMemo(
		() => ({ pendingCount, errorCount, syncedCount }),
		[pendingCount, errorCount, syncedCount],
	);

	return (
		<Drawer
			isOpen={isOpen}
			onOpenChange={(open: boolean) => !open && onClose()}
			placement="right"
			size="lg"
		>
			<DrawerContent>
				<DrawerHeader className="flex items-center justify-between gap-3">
					Cola de sincronizacion
					<Button size="sm" variant="flat" onPress={() => void refresh()}>
						Actualizar
					</Button>
				</DrawerHeader>
				<DrawerBody>
					<Card className="mb-4">
						<CardBody className="flex flex-row gap-4">
							<SyncBadge status="pending" />
							<SyncBadge status="synced" />
							<SyncBadge status="error" />
							<span>Pendings: {stats.pendingCount}</span>
							<span>Errores: {stats.errorCount}</span>
							<span>Sincronizados: {stats.syncedCount}</span>
						</CardBody>
					</Card>

					<Tabs aria-label="Estados de sync">
						<Tab key="queue" title="Operaciones">
							<Table aria-label="Operaciones pendientes" removeWrapper>
								<TableHeader>
									<TableColumn>Entidad</TableColumn>
									<TableColumn>Operacion</TableColumn>
									<TableColumn>Estado</TableColumn>
									<TableColumn>Reintentos</TableColumn>
								</TableHeader>
								<TableBody
									isLoading={isLoading}
									emptyContent="Sin operaciones en cola."
								>
									{operations.map((operation) => (
										<TableRow key={operation.id}>
											<TableCell>{operation.entity}</TableCell>
											<TableCell>{operation.operation}</TableCell>
											<TableCell>
												<SyncBadge status={operation.status} />
											</TableCell>
											<TableCell>{operation.retries}</TableCell>
										</TableRow>
									))}
								</TableBody>
							</Table>
						</Tab>
					</Tabs>
				</DrawerBody>
			</DrawerContent>
		</Drawer>
	);
}
