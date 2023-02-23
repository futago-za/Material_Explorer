import { convertFileSrc } from '@tauri-apps/api/tauri'
import { MaterialEntity } from "../utils/database_type";
import { db } from "../utils/database";

type Props = {
  material: MaterialEntity,
  update: () => Promise<void>,
  notification: (action: string) => void
}

const Card: React.FC<Props> = (props) => {
  const handleCopy = async (e: React.MouseEvent<HTMLElement>) => {
    e.stopPropagation();
    navigator.clipboard.writeText(props.material.blend_file_path);
    props.notification('copy');
  }

  const handleDelete = async (e: React.MouseEvent<HTMLElement>) => {
    e.stopPropagation();
    const result = await db.deleteMaterial(props.material);
    if (result == true) {
      props.update();
      props.notification('delete');
    }
  }

  return (
    <div className="card" style={{width: "18rem", backgroundColor: "#c4c4c4"}}>
      <img src={convertFileSrc(props.material.thumbnail_path)} alt="" />
      <div className="card-body">
        <h3 className="card-title">{props.material.material_name}</h3>
        <div className="row justify-content-between p-2">
          <button type="button" className="btn btn-primary col-4" onClick={handleCopy}>COPY</button>
          <button type="button" className="btn btn-danger col-4" onClick={handleDelete}>DELETE</button>
        </div>
      </div>
    </div>
  );
}

export default Card;