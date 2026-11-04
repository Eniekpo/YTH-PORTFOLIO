const CalculatorModule = (function () {
    let result = 0;

    function add(value) {
        result += value;
        displayResult();
    }

    function subtract(value) {
        result -= value;
        displayResult();
    }

    function displayResult() {
        document.getElementById('output').textContent = `Result: ${result}`;
    }

    return {
        add,
        subtract,
    };
})();

class Subject {
    constructor() {
        this.observers = [];
    }

    subscribe(observer) {
        this.observers.push(observer);
    }

    unsubscribe(observer) {
        this.observers = this.observers.filter(obs => obs !== observer);
    }

    notify() {
        this.observers.forEach(observer => observer.update());
    }
}

class Observer {
    constructor(name) {
        this.name = name;
    }

    update() {
        console.log(`${this.name} received notification!`);
    }
}

class Settings {
    constructor() {
        if (Settings.instance) {
            return Settings.instance;
        }
        this.configuration = {};
        Settings.instance = this;
    }

    set(key, value) {
        this.configuration[key] = value;
    }

    get(key) {
        return this.configuration[key];
    }
}

CalculatorModule.add(10);
CalculatorModule.subtract(5);