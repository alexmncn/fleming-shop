import { Injectable } from '@angular/core';
import { ImageApiService } from './image-api.service';
import { firstValueFrom } from 'rxjs';

export interface ImageData {
  id: string;        // UUID extraído de la URL
  blobUrl: string;   // URL temporal creada desde el Blob
}

@Injectable({
  providedIn: 'root'
})
export class ImageStorageService {
  // Cache temporal: image_id -> Blob URL
  private imageCache = new Map<string, string>();

  constructor(private imageApi: ImageApiService) {}

  /**
   * Extrae el UUID/id de la URL de la imagen
   */
  private extractIdFromUrl(url: string): string {
    const segments = url.split('/');
    return segments[segments.length - 1]; // último segmento = image_id
  }

  /**
   * Obtiene la imagen desde cache o la descarga del backend
   * Devuelve un Blob URL listo para usar en <img [src]>
   */
  async getImage(url: string): Promise<string | null> {
    const id = this.extractIdFromUrl(url);

    // Si ya está en cache, devolvemos el Blob URL
    if (this.imageCache.has(id)) {
      return this.imageCache.get(id)!;
    }

    // Si no está, la descargamos del backend
    try {
      const blob = await firstValueFrom(this.imageApi.getImageById(id));
      if (!blob) return null;

      // Creamos un Blob URL temporal y guardamos en cache
      const blobUrl = URL.createObjectURL(blob);
      this.imageCache.set(id, blobUrl);
      return blobUrl;
    } catch {
      return null;
    }
  }

  /**
   * Subida de imagen
   * @param file Archivo seleccionado
   * @param articleCodebar Código del artículo
   * @param isMain Si es principal
   */
  async uploadImage(file: File, articleCodebar: string, isMain: boolean): Promise<ImageData> {
    // Llamamos al API para subir la imagen
    const response = await firstValueFrom(this.imageApi.uploadArticleImage(articleCodebar, file, isMain));
    const id = this.extractIdFromUrl(response.image_url);

    // Descargamos el archivo para cachearlo
    const blob = await firstValueFrom(this.imageApi.getImageById(id));
    if (!blob) throw new Error('No se pudo obtener el archivo después de subirlo');

    const blobUrl = URL.createObjectURL(blob);
    this.imageCache.set(id, blobUrl);

    return { id, blobUrl };
  }

  /**
   * Permite limpiar toda la cache
   */
  clearCache(): void {
    // Liberamos los Blob URLs para evitar memory leaks
    this.imageCache.forEach(url => URL.revokeObjectURL(url));
    this.imageCache.clear();
  }
}