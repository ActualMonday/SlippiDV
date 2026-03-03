/**
 * Worker pool — persistent pool for parsing multiple Slippi files
 */

const { Worker } = require('worker_threads');
const path = require('path');
const os = require('os');

function createWorkerPool(slippiID, concurrency = os.cpus().length - 1) {
    const workers = [];
    const idleWorkers = [];
    const taskQueue = [];

    // Spawn persistent workers
    for (let i = 0; i < concurrency; i++) {
        const worker = new Worker(path.join(__dirname, 'worker.js'), { workerData: { slippiID } });
        worker.on('message', (msg) => {
            worker._resolve(msg); // resolve the promise for current task
            worker._resolve = null;
            if (taskQueue.length) assignNext(worker);
            else idleWorkers.push(worker);
        });
        workers.push(worker);
        idleWorkers.push(worker);
    }

    function assignNext(worker) {
        const task = taskQueue.shift();
        if (!task) {
            idleWorkers.push(worker);
            return;
        }
        worker._resolve = task.resolve;
        worker.postMessage(task.filePath);
    }

    function runTask(filePath) {
        return new Promise(resolve => {
            const worker = idleWorkers.shift();
            if (worker) {
                worker._resolve = resolve;
                worker.postMessage(filePath);
            } else {
                taskQueue.push({ filePath, resolve });
            }
        });
    }

    async function terminateAll() {
        await Promise.all(workers.map(w => w.terminate()));
    }

    return { runTask, terminateAll };
}

module.exports = { createWorkerPool };