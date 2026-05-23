// Bus de eventos nativo de bajo nivel para maxima reactividad
export const connectivityBus = new EventTarget();

export const emitConnectionRestored = () => {
	connectivityBus.dispatchEvent(new Event("connection-restored"));
};
