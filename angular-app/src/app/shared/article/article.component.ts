import { Component, Input, OnInit, signal, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { trigger, style, transition, animate, state} from '@angular/animations';
import { SkeletonModule } from 'primeng/skeleton';

import { Article } from '../../models/article.model';

import { AuthService } from '../../services/auth/auth.service';
import { MessageService } from '../../services/message/message.service';
import { ArticleActionsService } from '../../services/admin/actions/articles/article-actions.service';

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
      private http: HttpClient, 
      private messageService: MessageService, 
      private authService: AuthService, 
      private articleActionsService: ArticleActionsService
    ) { }

  ngOnInit(): void {
    this.authService.isAuthenticated$.subscribe((auth: boolean) => {
      this.isAuth.set(auth);
    });
  }

  ngOnChanges(): void {
    this.imgUrl.set(this.article.image_url);
    this.loading.set(!this.article.detalle);
    this.imgError.set(false);
    this.isFeatured.set(this.article.destacado);
    this.isHidden.set(this.article.hidden);
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

  uploadImage(): void {
    if (this.selectedFile()) {
      this.uploadingImage.set(true);

      const formData = new FormData();
      formData.append('file', this.selectedFile()!!, this.selectedFile.name);
      formData.append('codebar', this.article.codebar);
      formData.append('is_main', this.isUploadingImageMain() ? '1' : '0');

      this.http.post<{ image_url: string }>(this.uploadImageURL, formData)
        .subscribe({
          next: (response) => {
            this.imgUrl.set(response.image_url);
            console.log('Imagen subida correctamente:', response);
            this.uploadingImage.set(false);
            this.messageService.showMessage('success', 'La imagen se ha añadido correctamente')
            this.toggleSelection()
          },
          error: (error) => {
            console.log(error)
            this.uploadingImage.set(false);
            this.messageService.showMessage('error', 'Ha ocurrido un error al subir la imagen')
          }
        });
    }
  }

  get inStock(): boolean {
    if (this.article.stock > 0) {
      return true
    } else {return false}
  }

}
