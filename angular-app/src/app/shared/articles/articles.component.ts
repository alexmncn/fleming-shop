import { Component, Input  } from '@angular/core';
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
  @Input() articles: any[]= [];

  per_page: number = 20;
  page: number = 1;
  placeholders: Article[] = new Array(this.per_page).fill('');
}
