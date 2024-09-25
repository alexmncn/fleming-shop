import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FloatingMessageComponent } from './floating-message.component';

describe('FloatingMessageComponent', () => {
  let component: FloatingMessageComponent;
  let fixture: ComponentFixture<FloatingMessageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FloatingMessageComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(FloatingMessageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
