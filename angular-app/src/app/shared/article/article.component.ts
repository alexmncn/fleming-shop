import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Router, ActivatedRoute } from '@angular/router';
import { trigger, style, transition, animate, state} from '@angular/animations';
import { Observable } from 'rxjs';
import { SkeletonModule } from 'primeng/skeleton';

import { Article } from '../../models/article.model';

import { AuthService } from '../../services/auth/auth.service';
import { MessageService } from '../../services/message/message.service';

import { CapitalizePipe } from '../../pipes/capitalize/capitalize.pipe';

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
  loading: boolean = true;
  imgURL: string = '';
  imgError: boolean = false;
  articleSelected: boolean = false;
  isAuth: boolean = false;
  adminMenuActive: boolean = false;
  featureURL: string = environment.apiUrl + '/articles/feature';
  isFeatured: boolean = false;
  hideURL: string = environment.apiUrl + '/articles/hide';
  isHidden: boolean = false;
  uploadImageURL: string = environment.apiUrl + '/upload/articles/images';
  uploadImageMenuActive: boolean = false;
  selectedFile: File | null = null;
  uploadingImage: boolean = false;
  uploadImagePreview: string | ArrayBuffer | null = null;

  constructor(private http: HttpClient, private messageService: MessageService, private authService: AuthService, private router: Router, private route: ActivatedRoute) { }

  ngOnInit(): void {
    this.authService.isAuthenticated$.subscribe((auth: boolean) => {
      this.isAuth = auth;
    });
  }

  ngOnChanges(): void {
    this.loading = !this.article.detalle;
    this.imgError = false;
    this.imgURL = environment.articleImageRoute + this.article.codebar + '.webp';
    this.isFeatured = this.article.destacado;
    this.isHidden = this.article.hidden;
  }

  toggleSelection(): void {
    if (this.articleSelected) {
      this.articleSelected = false;
      this.adminMenuActive = false;
      this.uploadImageMenuActive = false;
    } else {
      if (!this.loading) {
        this.articleSelected = true;
      }
    }
  }

  toggleAdminMenu(): void {
    this.adminMenuActive = !this.adminMenuActive;
  }

  toggleFeaturedCheckbox(event: Event): void {
    event.preventDefault();

    const checkbox = event.target as HTMLInputElement;

    var confirmed = false;
    if (!this.isFeatured) {
      confirmed = confirm('Seguro que quieres destacar el articulo?');
    } else {
      confirmed = confirm('Seguro que quieres eliminar de destacados el articulo?');
    }
    if (confirmed) {
      this.featureArticle(!this.isFeatured)
        .subscribe({
          next: (response) => {
            this.article.destacado = !this.article.destacado;
            this.isFeatured = this.article.destacado;
            checkbox.checked = this.isFeatured;

            var s_message = '';
            if (this.isFeatured) {
              s_message = 'El articulo se ha destacado correctamente';
            } else {
              s_message = 'El articulo se ha eliminado de destacados correctamente';
            }
            this.messageService.showMessage('success', s_message)
            this.articleSelected = false;
          },
          error: (error) => {
            console.log(error)
            this.messageService.showMessage('error', 'Ha ocurrido un error al destacar el articulo')
          }
        });
    } else {
      this.messageService.showMessage('warn', 'Proceso abortado')
    }
  }

  featureArticle(newValue: boolean): Observable<any> {
    return this.http.post(this.featureURL, {},{params: {'codebar': this.article.codebar, 'featured': newValue}});
  }

  toggleHiddenCheckbox(event: Event): void {
    event.preventDefault();

    const checkbox = event.target as HTMLInputElement;

    var confirmed = false;
    if (!this.isHidden) {
      confirmed = confirm('Seguro que quieres ocultar el articulo?');
    } else {
      confirmed = confirm('Seguro que quieres eliminar de ocultos el articulo?');
    }
    if (confirmed) {
      this.hideArticle(!this.isHidden)
        .subscribe({
          next: (response) => {
            this.article.hidden = !this.article.hidden;
            this.isHidden = this.article.hidden;
            checkbox.checked = this.isHidden;

            var s_message = '';
            if (this.isHidden) {
              s_message = 'El articulo se ha ocultado correctamente';
            } else {
              s_message = 'El articulo se ha eliminado de ocultos correctamente';
            }
            this.messageService.showMessage('success', s_message)
            this.articleSelected = false;
          },
          error: (error) => {
            console.log(error)
            this.messageService.showMessage('error', 'Ha ocurrido un error al destacar el articulo')
          }
        });
    } else {
      this.messageService.showMessage('warn', 'Proceso abortado')
    }
  }

  hideArticle(newValue: boolean): Observable<any> {
    return this.http.post(this.hideURL, {},{params: {'codebar': this.article.codebar, 'hidden': newValue}});
  }

  toggleImageUploadMenu():void {
    this.uploadImageMenuActive = !this.uploadImageMenuActive;
    if (this.selectedFile) {
      this.cleanFileSelected();
    }
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.selectedFile = input.files[0];
    
      const reader = new FileReader();
      reader.onload = () => {
        this.uploadImagePreview = reader.result;
      };
      reader.readAsDataURL(this.selectedFile);
    }
  }

  cleanFileSelected(): void {
    this.selectedFile = null;
    this.uploadImagePreview = null;
  }

  uploadImage(): void {
    if (this.selectedFile) {
      this.uploadingImage = true;

      const formData = new FormData();
      formData.append('file', this.selectedFile, this.selectedFile.name);

      this.http.post(this.uploadImageURL, formData, {params: {'codebar': this.article.codebar}})
        .subscribe({
          next: (response) => {
            this.uploadingImage = false;
            this.messageService.showMessage('success', 'La imagen se ha añadido correctamente')
            this.toggleSelection()
          },
          error: (error) => {
            console.log(error)
            this.uploadingImage = false;
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

  get formatedPvp(): string {
    return this.article.pvp.toFixed(2);
  }

  get formatedPcosto(): string {
    return this.article.pcosto.toFixed(2);
  }

}
