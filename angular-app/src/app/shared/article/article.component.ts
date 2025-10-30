import { Component, inject, Input, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { trigger, style, transition, animate, state} from '@angular/animations';
import { SkeletonModule } from 'primeng/skeleton';

import { Article } from '../../models/article.model';

import { AuthService } from '../../services/auth/auth.service';
import { MessageService } from '../../services/message/message.service';
import { ArticleActionsService } from '../../services/admin/actions/articles/article-actions.service';
import { ImageStoreService } from '../../services/admin/actions/images/image-store.service';

import { CapitalizePipe } from '../../pipes/capitalize/capitalize-pipe';

import { environment } from '../../../environments/environment';

@Component({
    selector: 'app-article',
    imports: [CommonModule, SkeletonModule, CapitalizePipe],
    templateUrl: './article.component.html',
    styleUrl: './article.component.css',
    animations: [
        trigger('fadeIn', [
            state('void', style({
                opacity: 0
            })),
            transition(':enter', [
                animate('0.15s ease-out', style({
                    opacity: 1
                }))
            ]),
            transition(':leave', [
                animate('0.10s ease-in', style({
                    opacity: 0
                }))
            ])
        ]),
        trigger('slideInDown', [
            state('void', style({
                transform: 'scale(0.9)',
                opacity: 0
            })),
            transition(':enter', [
                animate('0.2s ease-out', style({
                    transform: 'scale(1)',
                    opacity: 1
                }))
            ]),
            transition(':leave', [
                animate('0.10s ease-in', style({
                    transform: 'scale(0.9)',
                    opacity: 0
                }))
            ])
        ])
    ]
})
export class ArticleComponent implements OnInit {
  @Input() article!: Article;
  @Input() gridDisplay: boolean = false;
  @Input() listDisplay: boolean = false;

  featureURL: string = environment.apiUrl + '/articles/feature';
  hideURL: string = environment.apiUrl + '/articles/hide';
  uploadImageURL: string = environment.apiUrl + '/images/articles/upload';

  loading = signal(true);
  imgError = signal(false);
  imgUrl = signal('');
  articleSelected = signal(false);
  isAuth = signal(false);
  adminMenuActive = signal(false);
  isFeatured = signal(false);
  isHidden = signal(false);
  uploadImageMenuActive = signal(false);
  selectedFile = signal<File | null>(null);
  uploadingImage = signal(false);
  uploadImagePreview = signal<string | ArrayBuffer | null>(null);
  isUploadingImageMain = signal(false);

  constructor( 
      private messageService: MessageService, 
      private authService: AuthService, 
      private articleActionsService: ArticleActionsService,
      private imageStoreService: ImageStoreService
    ) { }

  ngOnInit(): void {
    this.authService.isAuthenticated$.subscribe((auth: boolean) => {
      this.isAuth.set(auth);
    });
  }

  ngOnChanges(): void {
    this.loadMainImage();
    this.loading.set(!this.article.detalle);
    this.imgError.set(false);
    this.isFeatured.set(this.article.destacado);
    this.isHidden.set(this.article.hidden);
  }

  async loadMainImage(): Promise<void> {
    if (!this.article.image_url) return;

    this.uploadingImage.set(true);
    const blobUrl = await this.imageStoreService.getImage(this.article.image_url);
    if (blobUrl) {
      this.imgUrl.set(blobUrl);
    } else {
      this.imgError.set(false);
    }
    this.uploadingImage.set(false);
  }

  toggleSelection(): void {
    if (this.articleSelected()) {
      this.articleSelected.set(false);
      this.adminMenuActive.set(false);
      this.uploadImageMenuActive.set(false);
    } else {
      if (!this.loading()) {
        this.articleSelected.set(true);
      }
    }
  }

  toggleAdminMenu(): void {
    this.adminMenuActive.set(!this.adminMenuActive());
  }

  toggleFeatureArticle(event: Event): void {
    event.preventDefault();
    this.articleActionsService.toggleFeatured(this.article, updated => {;
      this.articleSelected.set(false);
      this.isFeatured.set(updated.destacado);
    });
  }

  toggleHiddenCheckbox(event: Event): void {
    event.preventDefault();
    this.articleActionsService.toggleHidden(this.article, updated => {
      this.articleSelected.set(false);
      this.isHidden.set(updated.hidden);
    });
  }

  toggleImageUploadMenu(): void {
    this.uploadImageMenuActive.set(!this.uploadImageMenuActive());
    if (this.selectedFile()) {
      this.cleanFileSelected();
    }
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.selectedFile.set(input.files[0]);
    
      const reader = new FileReader();
      reader.onload = () => {
        this.uploadImagePreview.set(reader.result);
      };
      reader.readAsDataURL(this.selectedFile()!!);
    }
  }

  cleanFileSelected(): void {
    this.selectedFile.set(null);
    this.uploadImagePreview.set(null);
  }

  toggleMainImage(event: Event): void {
    const checkbox = event.target as HTMLInputElement;
    this.isUploadingImageMain.set(checkbox.checked);
  }

  async uploadImage(): Promise<void> {
    if (!this.selectedFile()) return;

    this.uploadingImage.set(true);

    try {
      const { url } = await this.imageStoreService.uploadImage(
        this.selectedFile()!,
        this.article.codebar,
        this.isUploadingImageMain()
      );

      // Actualiza la información del artículo
      this.article.has_image = true;
      this.article.image_url = url;

      this.uploadingImage.set(false);
      
      // Recarga la imagen principal
      this.loadMainImage()

      this.messageService.showMessage('success', 'La imagen se ha añadido correctamente');
      this.toggleSelection();

    } catch (error) {
      console.error(error);
      this.uploadingImage.set(false);
      this.messageService.showMessage('error', 'Ha ocurrido un error al subir la imagen');
    }
  }

  get inStock(): boolean {
    if (this.article.stock > 0) {
      return true
    } else {return false}
  }

}
