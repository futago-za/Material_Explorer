import SQLite from "tauri-plugin-sqlite-api";
import { MaterialEntity } from "./database_type"
import { join, appDataDir } from "@tauri-apps/api/path";
import { createDir, exists, BaseDirectory } from "@tauri-apps/api/fs";

const DB_TABLE_NAME = "materials"
const DB_FILE_NAME = "material_explorer.db"
const APP_DATA_DIR_NAME = "material_explorer"

class DataBaseManager {
  static db: SQLite | undefined

  public static async build(): Promise<DataBaseManager> {
    const manager = new DataBaseManager();

    const appDataDirPath = await appDataDir();
    const db_data_directory = await join(appDataDirPath, APP_DATA_DIR_NAME);
    const isCreated = await exists(APP_DATA_DIR_NAME, { dir: BaseDirectory.AppData });
    if (!isCreated) {
      await createDir(APP_DATA_DIR_NAME, { dir: BaseDirectory.AppData, recursive: true });
    }
    const file_path = await join(db_data_directory, DB_FILE_NAME);
    DataBaseManager.db = await SQLite.open(file_path);

    const rows = await DataBaseManager.db!.select<Array<any>>(`SELECT * FROM sqlite_master WHERE TYPE='table' AND name='${DB_TABLE_NAME}'`);
    if (rows.length == 0) {
      // テーブルが存在しないので作成する
      await DataBaseManager.db!.execute(`CREATE TABLE ${DB_TABLE_NAME} (id integer primary key autoincrement, thumbnail_path TEXT, blend_file_path TEXT, material_name TEXT);`);
      console.log("Create")
    }
 
    return manager;
  }

  public async fetchMaterials(): Promise<MaterialEntity[]> {
    const rows = await DataBaseManager.db!.select<MaterialEntity[]>(`SELECT * From ${DB_TABLE_NAME}`);
    return rows;
  }

  public async insertMaterial(material: MaterialEntity): Promise<boolean> {
    const result = await DataBaseManager.db!.execute(`INSERT INTO ${DB_TABLE_NAME} VALUES (${material.thumbnail_path},${material.blend_file_path},${material.material_name})`);
    return result;
  }

  public async deleteMaterial(material: MaterialEntity): Promise<boolean> {
    const result = await DataBaseManager.db!.execute(`DELETE FROM ${DB_TABLE_NAME} WHERE id == ${material.id}`);
    console.log(result);
    return result;
  }
}

export const db = await DataBaseManager.build();
