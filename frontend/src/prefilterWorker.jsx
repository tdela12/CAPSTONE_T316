self.onmessage = (e) => {
  const result = heavyComputation(e.data);
  postMessage(result);
};
