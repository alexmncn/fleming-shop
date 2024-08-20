import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SkeletonModule } from 'primeng/skeleton';

import { Article } from '../../models/article.model';

import { CapitalizePipe } from '../../pipes/capitalize/capitalize.pipe';

@Component({
  selector: 'app-article',
  standalone: true,
  imports: [CommonModule, SkeletonModule, CapitalizePipe],
  templateUrl: './article.component.html',
  styleUrl: './article.component.css'
})
export class ArticleComponent {
  @Input() article!: Article;
  @Input() gridDisplay: boolean = false;
  @Input() listDisplay: boolean = false;
  loading: boolean = true;
  imgURL: string = '';
  imgError: boolean = false;

  ngOnChanges(): void {
    this.loading = !this.article.detalle;
    this.imgError = false;
    this.imgURL = '/assets/images/articles/' + this.article.ref + '.jpg';
  }

  showPlaceholder(): void {
    this.imgError = true;
  }

}
