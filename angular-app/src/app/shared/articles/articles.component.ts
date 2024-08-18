import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ArticleComponent } from '../article/article.component';
import { Article } from '../../models/article.model';

@Component({
  selector: 'app-articles',
  standalone: true,
  imports: [CommonModule, ArticleComponent],
  templateUrl: './articles.component.html',
  styleUrl: './articles.component.css'
})
export class ArticlesComponent {
  @Output() loadArticles = new EventEmitter();
  @Input() articles: any[]= [];
  @Input() totalArticles: number = 0;
  @Input() per_page: number = 20;
  @Input() loadingArticles: boolean = false;
  gridDisplay: boolean = true;
  listDisplay: boolean = false;
  placeholders: Article[] = new Array(this.per_page).fill('');

  load(): void {
    this.loadArticles.emit();
  }

  get allArticlesLoaded(): boolean {
    return this.articles.length === this.totalArticles;
  }

  setGridDisplay(): void {
    if (this.gridDisplay == false) {
      this.gridDisplay = true;
      this.listDisplay = false;
    }
  }

  setListDisplay(): void {
    if (this.listDisplay == false) {
      this.listDisplay = true;
      this.gridDisplay = false;
    }
  }

}
