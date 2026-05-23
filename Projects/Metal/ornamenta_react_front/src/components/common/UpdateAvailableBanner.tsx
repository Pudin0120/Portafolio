import { Button, Card, CardBody, Chip } from "@heroui/react";
import { RefreshCw } from "lucide-react";
import { useServiceWorker } from "@hooks/useServiceWorker";

export function UpdateAvailableBanner() {
	const { needRefresh, updateSW } = useServiceWorker();

	if (!needRefresh) return null;

	return (
		<div className="fixed bottom-4 right-4 z-[70] w-[min(92vw,24rem)]">
			<Card className="border-primary-200 bg-primary-50 shadow-lg">
				<CardBody className="flex flex-col gap-3 p-4">
					<div className="flex items-center gap-2">
						<Chip color="primary" variant="flat">
							Actualizacion disponible
						</Chip>
						<span className="text-sm font-medium text-primary-900">
							Hay una nueva version lista para cargarse.
						</span>
					</div>
					<p className="text-sm text-primary-800">
						Guarda tu work y recarga para ver los cambios mas recientes.
					</p>
					<div className="flex justify-end">
						<Button
							color="primary"
							variant="solid"
							startContent={<RefreshCw className="h-4 w-4" />}
							onPress={() => {
								updateSW();
							}}
						>
							Actualizar
						</Button>
					</div>
				</CardBody>
			</Card>
		</div>
	);
}
