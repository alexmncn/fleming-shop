import { Injectable, signal } from '@angular/core';

import { Article } from '../../../../models/article.model';

import { ArticleActionsApiService } from './article-actions-api.service'
import { CatalogStoreService } from '../../../catalog/catalog-store.service'; 
import { MessageService } from '../../../message/message.service';
import { firstValueFrom } from 'rxjs';


@Injectable({
  providedIn: 'root'
})
export class ArticleActionsService {
   loading = signal(false);

  constructor(private api: ArticleActionsApiService, private messageService: MessageService, private catalogStoreService: CatalogStoreService) {}

  async toggleFeatured(article: Article, update?: (a: Article) => void): Promise<void> {
    const newValue = !article.destacado;
    const confirmed = confirm(
      newValue
        ? '¿Seguro que quieres destacar el artículo?'
        : '¿Seguro que quieres eliminar de destacados el artículo?'
    );
    if (!confirmed) {
      this.messageService.showMessage('warn', 'Proceso abortado');
      return;
    }

    this.loading.set(true);
    try {
      await firstValueFrom(this.api.featureArticle(article.codebar, newValue));
      article.destacado = newValue;
      update?.(article);

      // Refrescar la lista de artículos destacados en el catálogo
      this.catalogStoreService.featuredArticles.loadTotal();
      this.catalogStoreService.featuredArticles.load(true);

      this.messageService.showMessage(
        'success',
        newValue
          ? 'El artículo se ha añadido a destacados correctamente'
          : 'El artículo se ha eliminado de destacados correctamente'
      );
    } catch (error) {
      console.error(error);
      this.messageService.showMessage('error', 'Ha ocurrido un error al destacar el artículo');
    } finally {
      this.loading.set(false);
    }
  }

  async toggleHidden(article: Article, update?: (a: Article) => void): Promise<void> {
    const newValue = !article.hidden;
    const confirmed = confirm(
      newValue
        ? '¿Seguro que quieres ocultar el artículo?'
        : '¿Seguro que quieres eliminar de ocultos el artículo?'
    );
    if (!confirmed) {
      this.messageService.showMessage('warn', 'Proceso abortado');
      return;
    }

    this.loading.set(true);
    try {
      await firstValueFrom(this.api.hideArticle(article.codebar, newValue));
      article.hidden = newValue;
      update?.(article);
      
      this.messageService.showMessage(
        'success',
        newValue
          ? 'El artículo se ha ocultado correctamente'
          : 'El artículo se ha eliminado de ocultos correctamente'
      );
    } catch (error) {
      console.error(error);
      this.messageService.showMessage(
        'error',
        'Ha ocurrido un error al ocultar el artículo'
      );
    } finally {
      this.loading.set(false);
    }
  }
}