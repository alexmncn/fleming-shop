import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { SkeletonModule } from 'primeng/skeleton';
import { trigger, style, transition, animate, state } from '@angular/animations';

import { CapitalizePipe } from '../../pipes/capitalize/capitalize-pipe';

import { CatalogStoreService } from '../../services/catalog/catalog-store.service';
import { Family } from '../../models/family.model';

@Component({
    selector: 'app-families-carousel',
    imports: [CommonModule, SkeletonModule, CapitalizePipe],
    templateUrl: './families-carousel.component.html',
    styleUrl: './families-carousel.component.css',
    animations: [
        trigger('arrowRotateLeft', [
            state('void', style({
                transform: 'rotate(180deg)',
            })),
            transition(':enter', [
                animate('0.25s ease-out', style({
                    transform: 'rotate(0deg)',
                }))
            ]),
            transition(':leave', [
                animate('0s ease-in', style({
                    opacity: 0
                }))
            ])
        ]),
        trigger('arrowRotateRight', [
            state('void', style({
                transform: 'rotate(-180deg)',
            })),
            transition(':enter', [
                animate('0.25s ease-out', style({
                    transform: 'rotate(0deg)',
                }))
            ]),
            transition(':leave', [
                animate('0s ease-in', style({
                    opacity: 0
                }))
            ])
        ])
    ]
})
export class FamiliesCarouselComponent implements OnInit {
  families = this.catalogStore.families.families;
  total = this.catalogStore.families.total;
  loading = this.catalogStore.families.loading;
  statusCode = this.catalogStore.families.statusCode;

  placeholders = signal<string[]>(new Array(20).fill(''));

  private isDragging = false;
  private startX = 0;
  private scrollLeft = 0;
  private scrollContainer: HTMLElement | null = null;
  private hasAnimated = false; // Para que solo se ejecute una vez
  private hoverAnimationTimeout: any = null;
  private dragStartX = 0;
  private dragStartY = 0;
  private hasDragged = false; // Para distinguir entre click y drag
  private clickedElement: HTMLElement | null = null;
  private isTouchDevice = false; // Para detectar dispositivos táctiles

  constructor(private catalogStore: CatalogStoreService, private router: Router) {
    // Detectar si es un dispositivo táctil
    this.isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  }

  ngOnInit(): void {
    if (this.catalogStore.families.families().length === 0) {
      this.catalogStore.families.loadTotal();
      this.catalogStore.families.load();
    }
  }

  
  onFamilyScroll(event: WheelEvent): void {
      const scrollContainer = event.currentTarget as HTMLElement;
      if (event.deltaY !== 0) {
        event.preventDefault();
        const scrollAmount = event.deltaY * 2;
        scrollContainer.scrollLeft += scrollAmount;
      }
  }


  onPointerDown(event: PointerEvent): void {
    const container = event.currentTarget as HTMLElement;
    
    // En dispositivos táctiles, no hacer nada - el click nativo y scroll funcionan correctamente
    if (this.isTouchDevice) return;
    
    const target = event.target as HTMLElement;
    
    // Guardar el elemento clickeado inicialmente
    this.clickedElement = target.closest('.family') as HTMLElement;
    this.scrollContainer = container;
    
    // Para desktop (mouse), inicializar variables de drag
    this.dragStartX = event.pageX;
    this.dragStartY = event.pageY;
    this.startX = event.pageX - container.offsetLeft;
    this.scrollLeft = container.scrollLeft;
    this.hasDragged = false;
    this.isDragging = false;
  }
  
  onPointerMove(event: PointerEvent): void {
    // En dispositivos táctiles, no usar drag personalizado
    if (this.isTouchDevice) return;
    
    if (!this.scrollContainer) return;
    
    // Calcular el desplazamiento desde el inicio
    const deltaX = Math.abs(event.pageX - this.dragStartX);
    const deltaY = Math.abs(event.pageY - this.dragStartY);
    
    // Solo activar el arrastre si el desplazamiento supera el umbral (5px)
    // y es mayor en horizontal que en vertical
    if (!this.isDragging && (deltaX > 5 || deltaY > 5)) {
      if (deltaX > deltaY) {
        this.isDragging = true;
        this.hasDragged = true;
        this.scrollContainer.setPointerCapture(event.pointerId);
        this.scrollContainer.style.cursor = 'grabbing';
      }
    }
    
    // Si ya estamos arrastrando, mover el scroll
    if (this.isDragging) {
      event.preventDefault();
      const x = event.pageX - this.scrollContainer.offsetLeft;
      const walk = (x - this.startX) * 2;
      this.scrollContainer.scrollLeft = this.scrollLeft - walk;
    }
  }
  
  onPointerUp(event: PointerEvent): void {
    if (!this.scrollContainer) return;
    
    // En dispositivos táctiles, no hacer nada - el click nativo y scroll funcionan correctamente
    if (this.isTouchDevice) {
      this.scrollContainer = null;
      this.clickedElement = null;
      return;
    }
    
    // Lógica para desktop (con mouse)
    // Si estábamos arrastrando, liberar la captura y prevenir el click
    if (this.isDragging) {
      event.preventDefault();
      this.scrollContainer.releasePointerCapture(event.pointerId);
      this.scrollContainer.style.cursor = 'grab';
    }
    
    this.isDragging = false;
    this.hasDragged = false;
    this.scrollContainer = null;
    this.clickedElement = null;
  }


  onMouseEnter(event: MouseEvent): void {
    // No ejecutar animación en dispositivos táctiles
    if (this.isTouchDevice || this.hasAnimated) return;
    
    const container = event.currentTarget as HTMLElement;
    
    // Verificar que hay contenido para hacer scroll
    if (container.scrollWidth <= container.clientWidth) return;
    
    // Delay pequeño antes de animar (opcional, para no ser intrusivo)
    this.hoverAnimationTimeout = setTimeout(() => {
      this.playHoverAnimation(container);
    }, 300); // 300ms de delay
  }

  onMouseLeave(event: MouseEvent): void {
    // Cancelar la animación si el usuario sale antes
    if (this.hoverAnimationTimeout) {
      clearTimeout(this.hoverAnimationTimeout);
      this.hoverAnimationTimeout = null;
    }
  }

  private playHoverAnimation(container: HTMLElement): void {
    if (this.isTouchDevice || this.hasAnimated) return;
    
    const initialScroll = container.scrollLeft;
    const scrollAmount = 30; // Píxeles a desplazar (ajusta según prefieras)
    const duration = 400; // Duración de cada movimiento en ms
    const easeOut = (t: number) => 1 - Math.pow(1 - t, 3); // Función de easing
    
    // Scroll hacia adelante
    this.animateScroll(container, initialScroll, initialScroll + scrollAmount, duration, easeOut, () => {
      // Scroll de vuelta
      this.animateScroll(container, initialScroll + scrollAmount, initialScroll, duration, easeOut, () => {
        this.hasAnimated = true;
      });
    });
  }

  private animateScroll(
    element: HTMLElement, 
    start: number, 
    end: number, 
    duration: number, 
    easing: (t: number) => number,
    callback?: () => void
  ): void {
    const startTime = performance.now();
    
    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easing(progress);
      
      element.scrollLeft = start + (end - start) * eased;
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      } else if (callback) {
        callback();
      }
    };
    
    requestAnimationFrame(animate);
  }

  navigateToFamily(family: Family): void {
    const slug = family.nomfam.toLowerCase().replace(/\s+/g, '-');
    this.router.navigate(['/catalog/family', `${family.codfam}-${slug}`]);
  }

  get noFamilies(): boolean {
    return this.statusCode() == 404 && this.families.length == 0 && !this.loading();
  }

  get serverError(): boolean {
    return (this.statusCode() == 408 || this.statusCode().toString().startsWith('5')) && this.families.length == 0 && !this.loading();
  }

}
