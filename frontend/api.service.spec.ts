import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ApiService } from './api.service';

describe('ApiService', () => {
  let service: ApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ApiService]
    });

    service = TestBed.inject(ApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should login and store token', () => {
    const mockResponse = { access_token: 'mock-token', job_title: 'Software Developer' };
    
    service.login('testuser', 'testpass', 'Software Developer').subscribe(response => {
      expect(response).toEqual(mockResponse);
      expect(localStorage.getItem('token')).toBe('mock-token');
      expect(localStorage.getItem('jobTitle')).toBe('Software Developer');
    });

    const req = httpMock.expectOne(`${service['apiUrl']}/login`);
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);
  });

  it('should send message', () => {
    const mockResponse = { message: 'AI response' };
    
    service.sendMessage('Hello').subscribe(response => {
      expect(response).toEqual(mockResponse);
    });

    const req = httpMock.expectOne(`${service['apiUrl']}/interview`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ message: 'Hello' });
    req.flush(mockResponse);
  });

  it('should logout and clear token', () => {
    localStorage.setItem('token', 'mock-token');
    localStorage.setItem('jobTitle', 'Software Developer');

    service.logout().subscribe(() => {
      expect(localStorage.getItem('token')).toBeNull();
      expect(localStorage.getItem('jobTitle')).toBeNull();
    });

    const req = httpMock.expectOne(`${service['apiUrl']}/logout`);
    expect(req.request.method).toBe('POST');
    req.flush({});
  });
});