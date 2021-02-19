class Truck extends Vehicle {
    constructor(x, y, flavor) {
        const initialMinSpeed = 400;
        const initialMaxSpeed = 750;
        const width = 1000;
        const tires = [
          {x1: 42, x2: 94, y1: 182, y2: 233, w: 474, h: 234, clearance: 2},
          {x1: 291, x2: 343, y1: 182, y2: 233, w: 474, h: 234, clearance: 2},
          {x1: 358, x2: 410, y1: 182, y2: 233, w: 474, h: 234, clearance: 2},
        ];
        const angularShake = 0.2;
        const yShake = 1.5;
        super('Truck', flavor, x, y, initialMinSpeed, initialMaxSpeed, width, tires, angularShake, yShake);
    }
}

ScActorManager.registerActor('Truck', Truck);
