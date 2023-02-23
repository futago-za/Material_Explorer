import { useState, useEffect, useCallback } from "react";
import { db } from "./utils/database";
import { MaterialEntity } from "./utils/database_type";
import Toast from 'react-bootstrap/Toast';
import Card from "./components/Card";
import { ToastContainer } from "react-bootstrap";

const App = () => {
  const [showCopyToast, setShowCopyToast] = useState(false);
  const [showDeleteToast, setShowDeleteToast] = useState(false);
  const [materials, setMaterials] = useState<MaterialEntity[]>();

  const updateMaterials = useCallback(async () => {
    const result = await db.fetchMaterials();
    setMaterials(result);
  }, []);

  const notifyAction = useCallback((action: string) => {
    if (action === 'copy') {
      setShowCopyToast(true);
    } else if (action === 'delete') {
      setShowDeleteToast(true);
    }
  }, []);

  useEffect(() => {
    (async() => updateMaterials())();
  }, []);

  return (
    <div className="container-fluid p-5">
      <ToastContainer position="top-end" className="p-3">
        <Toast onClose={() => setShowCopyToast(false)} show={showCopyToast} delay={10000} bg='info' autohide>
          <Toast.Header>
            <strong className="me-auto">Copy!</strong>
          </Toast.Header>
          <Toast.Body>Please use the copied content in Blender's append!</Toast.Body>
        </Toast>
      </ToastContainer>
      
      <ToastContainer position="top-end" className="p-3">
        <Toast onClose={() => setShowDeleteToast(false)} show={showDeleteToast} delay={10000} bg='danger' autohide>
          <Toast.Header>
            <strong className="me-auto">Delete!</strong>
          </Toast.Header>
          <Toast.Body>The material you selected has been deleted!</Toast.Body>
        </Toast>
      </ToastContainer>

      <button type="button" className="btn btn-success mb-4 p-2" onClick={updateMaterials}>UPDATE</button>
      <div className="row row-cols-auto gy-5">
        {
          materials?.length === 0 ? (
            <>
              <h3>None registered</h3>
            </>
          ) : (
          <>
            {
              materials?.map((material, index) => (
                <div className="col" key={index}>
                  <Card material={material} update={updateMaterials} notification={notifyAction} />
                </div>
              ))
            }
          </>
          )
        }
      </div>
    </div>
  );
}

export default App;
