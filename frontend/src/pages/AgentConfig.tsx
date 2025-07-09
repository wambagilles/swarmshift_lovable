import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Upload, Link2, FileText, ArrowLeft, Settings, Trash2, HelpCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useTranslation } from '@/hooks/useTranslation';

interface AgentConfigProps {
  onNavigate: (page: string) => void;
  agentId: string;
}

const AgentConfig: React.FC<AgentConfigProps> = ({ onNavigate, agentId }) => {
  const { t } = useTranslation();
  const [isLoading, setIsLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [urls, setUrls] = useState<string[]>(['']);
  const [embeddingModel, setEmbeddingModel] = useState('openai');
  const [llmModel, setLlmModel] = useState('gpt-3.5-turbo');
  const [splittingMethod, setSplittingMethod] = useState('recursive');

  // Mock existing documents
  const existingDocuments = [
    { id: 1, name: 'company-handbook.pdf', type: 'PDF', size: '2.4 MB' },
    { id: 2, name: 'api-documentation.pdf', type: 'PDF', size: '1.8 MB' },
    { id: 3, name: 'https://docs.example.com', type: 'URL', size: 'N/A' }
  ];

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const files = Array.from(e.dataTransfer.files).filter(
        file => file.type === 'application/pdf' || file.type.includes('word')
      );
      setUploadedFiles(prev => [...prev, ...files]);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files).filter(
        file => file.type === 'application/pdf' || file.type.includes('word')
      );
      setUploadedFiles(prev => [...prev, ...files]);
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const addUrlField = () => {
    setUrls(prev => [...prev, '']);
  };

  const updateUrl = (index: number, value: string) => {
    setUrls(prev => prev.map((url, i) => i === index ? value : url));
  };

  const removeUrl = (index: number) => {
    setUrls(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulate saving
    setTimeout(() => {
      setIsLoading(false);
      onNavigate('dashboard');
    }, 2000);
  };

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b border-border bg-card/50 backdrop-blur-sm">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-4 py-4">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => onNavigate('dashboard')}
              >
                <ArrowLeft className="h-4 w-4" />
                {t('agentConfig.backToAgents')}
              </Button>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-primary to-accent rounded-lg">
                  <Settings className="h-5 w-5 text-background" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-foreground">{t('agentConfig.title')}</h1>
                  <p className="text-sm text-muted-foreground">{t('agentConfig.subtitle')}</p>
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Agent Information */}
            <Card className="border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5 text-primary" />
                  {t('agentConfig.agentInfo')}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">{t('createAgent.agentName')} *</Label>
                  <Input
                    id="name"
                    defaultValue="Company Knowledge Assistant"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">{t('createAgent.description')}</Label>
                  <Textarea
                    id="description"
                    defaultValue="AI assistant for company documentation"
                    rows={3}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Model Settings */}
            <Card className="border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5 text-accent" />
                  {t('agentConfig.modelSettings')}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label>{t('createAgent.embeddingModel')}</Label>
                      <Tooltip>
                        <TooltipTrigger>
                          <HelpCircle className="h-4 w-4 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent>
                          <p className="max-w-xs">{t('createAgent.embeddingModelHelp')}</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Select value={embeddingModel} onValueChange={setEmbeddingModel}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="openai">OpenAI</SelectItem>
                        <SelectItem value="huggingface">HuggingFace</SelectItem>
                        <SelectItem value="cohere">Cohere</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label>{t('createAgent.llmModel')}</Label>
                      <Tooltip>
                        <TooltipTrigger>
                          <HelpCircle className="h-4 w-4 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent>
                          <p className="max-w-xs">{t('createAgent.llmModelHelp')}</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Select value={llmModel} onValueChange={setLlmModel}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                        <SelectItem value="gpt-4">GPT-4</SelectItem>
                        <SelectItem value="claude-3-sonnet">Claude 3 Sonnet</SelectItem>
                        <SelectItem value="llama-2">Llama 2</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label>{t('createAgent.splittingMethod')}</Label>
                      <Tooltip>
                        <TooltipTrigger>
                          <HelpCircle className="h-4 w-4 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent>
                          <p className="max-w-xs">{t('createAgent.splittingMethodHelp')}</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Select value={splittingMethod} onValueChange={setSplittingMethod}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="recursive">Recursive</SelectItem>
                        <SelectItem value="character">Character</SelectItem>
                        <SelectItem value="token">Token</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Document Management */}
            <Card className="border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-accent" />
                  {t('agentConfig.documentManagement')}
                </CardTitle>
                <CardDescription>
                  {t('agentConfig.documentManagementDesc')}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="existing" className="space-y-4">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="existing">{t('agentConfig.existingDocuments')}</TabsTrigger>
                    <TabsTrigger value="add">{t('agentConfig.addDocuments')}</TabsTrigger>
                  </TabsList>

                  <TabsContent value="existing" className="space-y-4">
                    {existingDocuments.length > 0 ? (
                      <div className="space-y-2">
                        {existingDocuments.map((doc) => (
                          <div
                            key={doc.id}
                            className="flex items-center justify-between p-3 bg-muted rounded-lg"
                          >
                            <div className="flex items-center gap-3">
                              <FileText className="h-4 w-4 text-primary" />
                              <span className="text-sm font-medium text-foreground">
                                {doc.name}
                              </span>
                              <Badge variant="secondary">{doc.type}</Badge>
                              <Badge variant="outline">{doc.size}</Badge>
                            </div>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="text-destructive hover:text-destructive-foreground hover:bg-destructive"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        {t('agentConfig.noDocuments')}
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="add" className="space-y-4">
                    <Tabs defaultValue="upload" className="space-y-4">
                      <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="upload">{t('createAgent.uploadDocs')}</TabsTrigger>
                        <TabsTrigger value="urls">{t('createAgent.addUrls')}</TabsTrigger>
                      </TabsList>

                      <TabsContent value="upload" className="space-y-4">
                        <div
                          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                            dragActive
                              ? 'border-primary bg-primary/5'
                              : 'border-muted hover:border-primary/50'
                          }`}
                          onDragEnter={handleDrag}
                          onDragLeave={handleDrag}
                          onDragOver={handleDrag}
                          onDrop={handleDrop}
                        >
                          <Upload className="h-10 w-10 text-muted-foreground mx-auto mb-4" />
                          <h3 className="text-lg font-semibold text-foreground mb-2">
                            {t('createAgent.dropFiles')}
                          </h3>
                          <p className="text-muted-foreground mb-4">
                            {t('createAgent.clickToBrowse')}
                          </p>
                          <input
                            type="file"
                            accept=".pdf,.doc,.docx"
                            multiple
                            onChange={handleFileUpload}
                            className="hidden"
                            id="file-upload"
                          />
                          <Button 
                            type="button" 
                            variant="outline"
                            onClick={() => document.getElementById('file-upload')?.click()}
                          >
                            {t('createAgent.selectFiles')}
                          </Button>
                        </div>

                        {uploadedFiles.length > 0 && (
                          <div className="space-y-2">
                            <h4 className="font-medium text-foreground">{t('createAgent.uploadedFiles')}</h4>
                            <div className="space-y-2">
                              {uploadedFiles.map((file, index) => (
                                <div
                                  key={index}
                                  className="flex items-center justify-between p-3 bg-muted rounded-lg"
                                >
                                  <div className="flex items-center gap-3">
                                    <FileText className="h-4 w-4 text-primary" />
                                    <span className="text-sm font-medium text-foreground">
                                      {file.name}
                                    </span>
                                    <Badge variant="secondary">
                                      {(file.size / 1024 / 1024).toFixed(1)} MB
                                    </Badge>
                                  </div>
                                  <Button
                                    type="button"
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => removeFile(index)}
                                    className="text-destructive hover:text-destructive-foreground hover:bg-destructive"
                                  >
                                    {t('createAgent.remove')}
                                  </Button>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </TabsContent>

                      <TabsContent value="urls" className="space-y-4">
                        <div className="space-y-4">
                          {urls.map((url, index) => (
                            <div key={index} className="flex gap-2">
                              <div className="flex-1">
                                <Input
                                  placeholder={t('createAgent.urlPlaceholder')}
                                  value={url}
                                  onChange={(e) => updateUrl(index, e.target.value)}
                                />
                              </div>
                              {urls.length > 1 && (
                                <Button
                                  type="button"
                                  variant="outline"
                                  size="sm"
                                  onClick={() => removeUrl(index)}
                                >
                                  {t('createAgent.remove')}
                                </Button>
                              )}
                            </div>
                          ))}
                          <Button
                            type="button"
                            variant="outline"
                            onClick={addUrlField}
                            className="w-full"
                          >
                            <Link2 className="h-4 w-4" />
                            {t('createAgent.addAnotherUrl')}
                          </Button>
                        </div>
                      </TabsContent>
                    </Tabs>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>

            {/* Submit */}
            <div className="flex justify-end gap-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => onNavigate('dashboard')}
              >
                {t('createAgent.cancel')}
              </Button>
              <Button
                type="submit"
                variant="hero"
                disabled={isLoading}
                className="min-w-32"
              >
                {isLoading ? t('agentConfig.saving') : t('agentConfig.saveChanges')}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </TooltipProvider>
  );
};

export default AgentConfig;