import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SkeletonModule } from 'primeng/skeleton';
import { trigger, style, transition, animate, state } from '@angular/animations';

import { Article } from '../../models/article.model';

import { CapitalizePipe } from '../../pipes/capitalize/capitalize.pipe';

@Component({
  selector: 'app-article',
  standalone: true,
  imports: [CommonModule, SkeletonModule, CapitalizePipe],
  templateUrl: './article.component.html',
  styleUrl: './article.component.css',
  animations:[
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
        animate('0.250s ease-in', style({
          transform: 'scale(0.9)',
          opacity: 0
        }))
      ])
    ])
  ]
})
export class ArticleComponent {
  @Input() article!: Article;
  @Input() gridDisplay: boolean = false;
  @Input() listDisplay: boolean = false;
  loading: boolean = true;
  imgURL: string = '';
  imgError: boolean = false;
  selected: boolean = false;

  ngOnChanges(): void {
    this.loading = !this.article.detalle;
    this.imgError = false;
    this.imgURL = '/assets/images/articles/' + this.article.ref + '.jpg';
  }

  showPlaceholder(): void {
    this.imgError = true;
  }

  toggleSelection(): void {
    if (this.selected) {
      this.selected = false;
    } else {
      this.selected = true;
    }
  }

  get inStock(): boolean {
    if (this.article.stock > 0) {
      return true
    } else {return false}
  }

}
