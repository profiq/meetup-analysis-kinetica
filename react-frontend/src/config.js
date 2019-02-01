// This is url to your local instance of Kinetica GPUDB
export const gpuURL = "http://localhost:9191";

// We imported the Kinetita JS APU library by just putting that file into /public folder.
export const gpudb = new window.GPUdb(gpuURL);

export default gpudb;




