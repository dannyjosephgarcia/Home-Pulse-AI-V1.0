import React, { useEffect, useState } from 'react';
import Index from './pages/Index'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <Index />
    </div>
  );
}

export default App;
