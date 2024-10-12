import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
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
  standalone: true,
  imports: [CommonModule, SkeletonModule, CapitalizePipe],
  templateUrl: './article.component.html',
  styleUrl: './article.component.css',
  animations:[
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

  constructor(private http: HttpClient, private messageService: MessageService, private authService: AuthService) { }

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
  }

  showPlaceholder(): void {
    this.imgError = true;
  }

  toggleSelection(): void {
    if (this.articleSelected) {
      this.articleSelected = false;
      this.adminMenuActive = false;
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
    console.log(this.article.codebar)
    return this.http.post(this.featureURL, {},{params: {'codebar': this.article.codebar, 'featured': newValue}});
  }

  get inStock(): boolean {
    if (this.article.stock > 0) {
      return true
    } else {return false}
  }

  get formatedPvp(): string {
    return this.article.pvp.toFixed(2);
  }

}
